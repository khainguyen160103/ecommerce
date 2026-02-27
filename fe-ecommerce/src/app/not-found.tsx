import { Button, Result } from "antd";
import Link from "next/link";


export default function NotFound() { 
  return (  <Result
        status="403"
        title="403"
        subTitle="Sorry, you are not authorized to access this page."
        extra={<Button href="/home" type="primary">Back Home</Button>}
    />)
}