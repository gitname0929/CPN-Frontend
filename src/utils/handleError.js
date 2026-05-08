import {
    Notification
} from "element-ui"

const handleErrorMessage = (error) => {
    if (error.response) {
        // error.response包含了服务器响应的详细信息
        const statusCode = error.response.status;
        const errorMessage = error.response.data.message;
        // 根据不同的错误代码，显示不同的错误消息
        Notification.error(`${statusCode}: ${errorMessage}`);
    } else {
        // 其他错误（例如网络问题）
        Notification.error(`${error}`);
        console.log(error);
    }
}

export default handleErrorMessage