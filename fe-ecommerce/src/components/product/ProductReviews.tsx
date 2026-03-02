'use client'
import { useState } from 'react'
import { Rate, Button, Input, Card, Avatar, Progress, Divider, Empty, Modal, Space } from 'antd'
import { UserOutlined, EditOutlined, DeleteOutlined, StarFilled } from '@ant-design/icons'
import { useReview } from '@/hook/useReview'
import { Review, ReviewSummary } from '@/models/review'

const { TextArea } = Input

function formatDate(dateStr: string) {
  const d = new Date(dateStr)
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

// ==================== REVIEW SUMMARY ====================

function ReviewSummaryCard({ summary }: { summary: ReviewSummary }) {
  const { avg_rating, total_reviews, distribution } = summary

  return (
    <div className="flex gap-8 items-center flex-wrap">
      {/* Điểm trung bình */}
      <div className="text-center min-w-30">
        <div className="text-5xl font-bold text-orange-500">{avg_rating}</div>
        <Rate disabled allowHalf value={avg_rating} className="text-sm mt-1" />
        <div className="text-gray-500 mt-1">{total_reviews} đánh giá</div>
      </div>

      {/* Phân bố sao */}
      <div className="flex-1 min-w-62.5">
        {[5, 4, 3, 2, 1].map((star) => {
          const count = distribution[star] || 0
          const percent = total_reviews > 0 ? (count / total_reviews) * 100 : 0
          return (
            <div key={star} className="flex items-center gap-2 mb-1">
              <span className="w-12.5 text-sm text-right flex items-center justify-end gap-1">
                {star} <StarFilled className="text-orange-400 text-xs" />
              </span>
              <Progress
                percent={percent}
                showInfo={false}
                strokeColor="#f59e0b"
                trailColor="#f3f4f6"
                size="small"
                className="flex-1"
              />
              <span className="w-7.5 text-sm text-gray-500">{count}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ==================== REVIEW FORM ====================

function ReviewForm({
  productId,
  existingReview,
  onCancel,
}: {
  productId: string
  existingReview?: Review | null
  onCancel?: () => void
}) {
  const [rating, setRating] = useState(existingReview?.rating || 0)
  const [comment, setComment] = useState(existingReview?.comment || '')
  const { createReview, updateReview } = useReview(productId)

  const isEditing = !!existingReview

  const handleSubmit = () => {
    if (rating === 0) {
      return
    }

    if (isEditing && existingReview) {
      updateReview.mutate(
        { reviewId: existingReview.id, data: { rating, comment: comment || undefined } },
        { onSuccess: () => onCancel?.() }
      )
    } else {
      createReview.mutate(
        { productId, data: { rating, comment: comment || undefined } },
        { onSuccess: () => { setRating(0); setComment('') } }
      )
    }
  }

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <h4 className="font-semibold mb-3">
        {isEditing ? 'Chỉnh sửa đánh giá' : 'Viết đánh giá'}
      </h4>
      <div className="mb-3">
        <span className="mr-2 text-sm text-gray-600">Đánh giá của bạn:</span>
        <Rate value={rating} onChange={setRating} />
      </div>
      <TextArea
        rows={3}
        placeholder="Chia sẻ trải nghiệm của bạn về sản phẩm..."
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        maxLength={500}
        showCount
        className="mb-3"
      />
      <Space>
        <Button
          type="primary"
          onClick={handleSubmit}
          loading={createReview.isPending || updateReview.isPending}
          disabled={rating === 0}
        >
          {isEditing ? 'Cập nhật' : 'Gửi đánh giá'}
        </Button>
        {onCancel && (
          <Button onClick={onCancel}>Hủy</Button>
        )}
      </Space>
    </div>
  )
}

// ==================== REVIEW ITEM ====================

function ReviewItem({
  review,
  currentUserId,
  productId,
}: {
  review: Review
  currentUserId?: string
  productId: string
}) {
  const [isEditing, setIsEditing] = useState(false)
  const { deleteReview } = useReview(productId)
  const isOwner = currentUserId === review.user_id

  const handleDelete = () => {
    Modal.confirm({
      title: 'Xóa đánh giá',
      content: 'Bạn có chắc chắn muốn xóa đánh giá này?',
      okText: 'Xóa',
      cancelText: 'Hủy',
      okType: 'danger',
      onOk: () => deleteReview.mutate(review.id),
    })
  }

  if (isEditing) {
    return (
      <ReviewForm
        productId={productId}
        existingReview={review}
        onCancel={() => setIsEditing(false)}
      />
    )
  }

  return (
    <div className="py-4">
      <div className="flex items-start gap-3">
        <Avatar icon={<UserOutlined />} className="bg-blue-500 shrink-0" />
        <div className="flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-semibold text-sm">{review.username}</span>
            <Rate disabled value={review.rating} className="text-xs" />
            <span className="text-xs text-gray-400">
              {formatDate(review.create_at)}
            </span>
          </div>
          {review.comment && (
            <p className="text-gray-700 mt-1 text-sm">{review.comment}</p>
          )}
          {isOwner && (
            <Space className="mt-2" size="small">
              <Button
                type="link"
                size="small"
                icon={<EditOutlined />}
                onClick={() => setIsEditing(true)}
              >
                Sửa
              </Button>
              <Button
                type="link"
                size="small"
                danger
                icon={<DeleteOutlined />}
                onClick={handleDelete}
                loading={deleteReview.isPending}
              >
                Xóa
              </Button>
            </Space>
          )}
        </div>
      </div>
    </div>
  )
}

// ==================== MAIN COMPONENT ====================

export default function ProductReviews({
  productId,
  currentUserId,
}: {
  productId: string
  currentUserId?: string
}) {
  const { reviewsData, myReviewData } = useReview(productId)

  const reviews: Review[] = reviewsData.data?.data || []
  const summary: ReviewSummary = reviewsData.data?.summary || {
    avg_rating: 0,
    total_reviews: 0,
    distribution: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 },
  }
  const myReview: Review | null = myReviewData.data?.data || null

  return (
    <Card title="Đánh giá sản phẩm" className="shadow-sm">
      {/* Tổng quan đánh giá */}
      {summary.total_reviews > 0 && (
        <>
          <ReviewSummaryCard summary={summary} />
          <Divider />
        </>
      )}

      {/* Form viết đánh giá (chỉ hiện khi đã đăng nhập và chưa đánh giá) */}
      {currentUserId && !myReview && (
        <>
          <ReviewForm productId={productId} />
          <Divider />
        </>
      )}

      {/* Danh sách đánh giá */}
      {reviews.length > 0 ? (
        <div className="divide-y divide-gray-100">
          {reviews.map((review) => (
            <ReviewItem
              key={review.id}
              review={review}
              currentUserId={currentUserId}
              productId={productId}
            />
          ))}
        </div>
      ) : (
        <Empty
          description="Chưa có đánh giá nào"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      )}
    </Card>
  )
}
