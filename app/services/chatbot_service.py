"""
Chatbot Service - Tích hợp Groq AI (Llama) với function calling
Hỗ trợ streaming response qua WebSocket
"""
import json
import re
import logging
from typing import AsyncGenerator
from groq import Groq, BadRequestError
from sqlmodel import Session, select, or_
from sqlalchemy.orm import selectinload

from app.core.settings import settings
from app.models.product_model import Product
from app.models.category_model import Category
from app.services.chatbot_prompt import SYSTEM_PROMPT, FUNCTION_DECLARATIONS

logger = logging.getLogger(__name__)


# Chuyển đổi function declarations sang format OpenAI tools
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": f["name"],
            "description": f["description"],
            "parameters": f["parameters"],
        },
    }
    for f in FUNCTION_DECLARATIONS
]


class ChatbotService:
    """Service xử lý chatbot AI với Groq (Llama 3)"""

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    def _execute_function(self, function_name: str, function_args: dict, session: Session) -> str:
        """Thực thi function call và trả về kết quả dạng string"""
        if function_name == "search_products":
            return self._search_products(function_args.get("keyword", ""), session)
        elif function_name == "get_product_detail":
            return self._get_product_detail(function_args.get("product_id", ""), session)
        elif function_name == "get_categories":
            return self._get_categories(session)
        else:
            return json.dumps({"error": f"Unknown function: {function_name}"})

    def _search_products(self, keyword: str, session: Session) -> str:
        """Tìm kiếm sản phẩm theo từ khóa"""
        stmt = (
            select(Product)
            .options(selectinload(Product.images))
            .where(
                or_(
                    Product.name.ilike(f"%{keyword}%"),
                    Product.description.ilike(f"%{keyword}%"),
                )
            )
            .limit(10)
        )
        products = session.exec(stmt).all()

        if not products:
            return json.dumps(
                {"message": f"Không tìm thấy sản phẩm nào với từ khóa '{keyword}'", "products": []},
                ensure_ascii=False,
            )

        result = []
        for p in products:
            image_url = p.images[0].url if p.images else None
            result.append({
                "id": str(p.id),
                "name": p.name,
                "price": p.price,
                "description": p.description,
                "image_url": image_url,
                "category_id": str(p.category_id),
            })

        return json.dumps({"products": result, "total": len(result)}, ensure_ascii=False)

    def _get_product_detail(self, product_id: str, session: Session) -> str:
        """Lấy chi tiết sản phẩm theo ID"""
        try:
            stmt = (
                select(Product)
                .options(
                    selectinload(Product.images),
                    selectinload(Product.product_details),
                )
                .where(Product.id == product_id)
            )
            product = session.exec(stmt).first()

            if not product:
                return json.dumps({"error": "Không tìm thấy sản phẩm"}, ensure_ascii=False)

            details = []
            for d in product.product_details:
                details.append({
                    "color": d.color,
                    "size": d.size,
                    "stock": d.stock,
                    "weight": d.weight,
                })

            images = [img.url for img in product.images]

            return json.dumps({
                "id": str(product.id),
                "name": product.name,
                "price": product.price,
                "description": product.description,
                "images": images,
                "details": details,
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"Lỗi khi lấy chi tiết sản phẩm: {str(e)}"}, ensure_ascii=False)

    def _get_categories(self, session: Session) -> str:
        """Lấy danh sách tất cả danh mục"""
        categories = session.exec(select(Category)).all()
        result = [
            {
                "id": str(c.id),
                "name": c.name,
                "description": c.description,
            }
            for c in categories
        ]
        return json.dumps({"categories": result}, ensure_ascii=False)

    def _build_messages(self, history: list) -> list[dict]:
        """Chuyển đổi history từ client thành format OpenAI messages"""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in history:
            role = msg.get("role", "user")
            if role == "assistant":
                messages.append({"role": "assistant", "content": msg.get("content", "")})
            else:
                messages.append({"role": "user", "content": msg.get("content", "")})
        return messages

    def _parse_failed_generation(self, failed_gen: str) -> list[tuple[str, dict]]:
        """
        Parse malformed tool calls from Llama models.
        Format: <function=function_name{"key": "value"}</function>
        Returns list of (function_name, args_dict) tuples.
        """
        pattern = r'<function=(\w+)(.*?)</function>'
        matches = re.findall(pattern, failed_gen, re.DOTALL)
        results = []
        for fn_name, fn_args_str in matches:
            fn_args_str = fn_args_str.strip()
            try:
                fn_args = json.loads(fn_args_str) if fn_args_str else {}
            except json.JSONDecodeError:
                logger.warning("Could not parse function args: %s", fn_args_str)
                fn_args = {}
            results.append((fn_name, fn_args))
        return results

    async def stream_chat(
        self, message: str, history: list, session: Session
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat response từ Groq.
        Xử lý function calling tự động.
        Yields từng chunk text.
        """
        # Build messages
        messages = self._build_messages(history)
        messages.append({"role": "user", "content": message})

        # Vòng lặp xử lý function calling (có thể cần nhiều lượt)
        max_iterations = 5
        for _ in range(max_iterations):
            try:
                # Gọi non-streaming để check có function call không
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto",
                    max_tokens=1024,
                    temperature=0.7,
                    stream=False,
                )
            except BadRequestError as e:
                # Llama đôi khi tạo tool call sai format → parse thủ công
                error_body = e.body
                if isinstance(error_body, dict):
                    error_info = error_body.get("error", {})
                    if error_info.get("code") == "tool_use_failed":
                        failed_gen = error_info.get("failed_generation", "")
                        logger.warning("Tool use failed, parsing manually: %s", failed_gen)
                        parsed_calls = self._parse_failed_generation(failed_gen)
                        if parsed_calls:
                            # Thực thi các function và thu thập kết quả
                            fn_context_parts = []
                            for fn_name, fn_args in parsed_calls:
                                fn_result = self._execute_function(fn_name, fn_args, session)
                                fn_context_parts.append(
                                    f"[Function {fn_name}({json.dumps(fn_args, ensure_ascii=False)})] "
                                    f"Result: {fn_result}"
                                )

                            # Inject kết quả vào context và gọi lại KHÔNG có tools
                            messages.append({
                                "role": "assistant",
                                "content": "Tôi đã tra cứu thông tin cho bạn.",
                            })
                            messages.append({
                                "role": "user",
                                "content": (
                                    "Dưới đây là kết quả tra cứu, hãy trả lời dựa trên dữ liệu này:\n"
                                    + "\n".join(fn_context_parts)
                                ),
                            })

                            # Stream final response without tools
                            stream = self.client.chat.completions.create(
                                model=self.model,
                                messages=messages,
                                max_tokens=1024,
                                temperature=0.7,
                                stream=True,
                            )
                            for chunk in stream:
                                delta = chunk.choices[0].delta
                                if delta and delta.content:
                                    yield delta.content
                            return
                # Nếu không phải tool_use_failed thì raise lại
                raise

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # Nếu có function call → thực thi rồi loop lại
            if tool_calls:
                # Sanitize: chỉ giữ các field Groq hỗ trợ, loại bỏ annotations etc.
                assistant_msg = {
                    "role": "assistant",
                    "content": response_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in tool_calls
                    ],
                }
                messages.append(assistant_msg)

                for tool_call in tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)

                    # Thực thi function
                    fn_result = self._execute_function(fn_name, fn_args, session)

                    # Thêm tool result vào messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": fn_result,
                    })

                # Tiếp tục loop để Groq xử lý kết quả function
                continue

            # Không có function call → stream response text
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
                stream=True,
            )

            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content

            break


# Singleton instance
chatbot_service = ChatbotService()
