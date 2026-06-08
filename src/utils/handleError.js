import {
    Notification
} from "element-ui"

const handleErrorMessage = (error) => {
    if (error.response) {
        // error.response包含了服务器响应的详细信息
        const statusCode = error.response.status;
        const data = error.response.data || {};
        const errorMessage = data.msg || data.message || data.error || error.response.statusText || '请求失败';
        // 根据不同的错误代码，显示不同的错误消息
        Notification.error(`${statusCode}: ${errorMessage}`);
    } else {
        // 其他错误（例如网络问题）
        Notification.error(`${error}`);
        console.log(error);
    }
}

export default handleErrorMessage
