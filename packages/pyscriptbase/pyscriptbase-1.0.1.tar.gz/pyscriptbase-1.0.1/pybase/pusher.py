import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from . import env as Env


class HtmlTableEmail:
    """
    HTML表格对象
    @headers=列数
    @rows=函数 不足自动补充空字符串 多余则忽略 [str|int|tuple] tuple=(str|int,G|R)有颜色
    @extras 末尾额外信息
    """

    def __init__(self, title: str, headers: list[str] = [], appendIndex: bool = True):
        self.title = title
        self.headers: list[str] = headers
        self.rows: list[str | int] = []
        self.extras: list[str] = []
        self.appendIndex = appendIndex

    def toStr(self) -> str:
        result = ""
        for index, row in enumerate(self.rows):
            result += f"[{index+1}] "
            for i in range(len(row)):
                if isinstance(row[i], tuple) and len(row[i]) >= 1:
                    result += f"{row[i][0]} "
                else:
                    result += f"{row[i]} "
            result += "\n"
        for extra in self.extras:
            result += f"\n{extra}\n"
        return result

    def toHtml(self) -> str:
        table = self
        thead = ""
        tbody = ""
        extras = ""

        if table.appendIndex:
            thead += "<th></th>"
        for header in table.headers:
            thead += f"<th>{header}</th>"

        for index, row in enumerate(table.rows):
            trs = ""
            if table.appendIndex:
                trs += f"<td>{index+1}</td>"
            for i in range(len(table.headers)):
                if len(row) - 1 >= i:
                    if isinstance(row[i], tuple) and len(row[i]) >= 2:
                        # 颜色
                        if str(row[i][1]).upper in ["G", "GREEN"]:
                            trs += f"<td class='green'>{row[i][0]}</td>"
                        else:
                            trs += f"<td class='red'>{row[i][0]}</td>"
                    else:
                        # 常规
                        trs += f"<td>{row[i]}</td>"
                else:
                    trs += "<td></td>"
            tbody += f"<tr>{trs}</tr>"

        if table.extras:
            extras = '<tr><th colspan="$$spans$$">其他报告</th></tr>'
            for extra in table.extras:
                extras += f'<tr><td colspan="$$spans$$">{extra}</td></tr>'

        html = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8" />
        <title></title>
        <style>
        table {
            width: 100%; /* 设置表格宽度 */
            margin: auto; /* 表格居中 */
            border-collapse: collapse; /* 边框合并 */
            font-size: 14px;
            text-align: center; /* 文本居中 */
        }
        th,
        td {
            padding: 10px; /* 内边距 */
            border: 1px solid #ddd; /* 边框样式 */
        }
        th {
            background-color: #f2f2f2; /* 表头背景颜色 */
        }
        tr:nth-child(even) {
            background-color: #f9f9f9; /* 隔行变色 */
        }
        caption {
            font-size: 1.5em;
            margin-bottom: 10px;
        }
        .green {
            color: green; /* 绿色文本 */
        }
        .red {
            color: red; /* 红色文本 */
        }
        </style>
    </head>
    <body>
        <table>
        <thead><tr>$$thead$$</tr></thead>
        <tbody>
        $$tbody$$
        $$extras$$
        </tbody>
        </table>
    </body>
    </html>
    """
        spans = len(table.headers) + (1 if table.appendIndex else 0)
        html = html.replace("$$thead$$", thead)
        html = html.replace("$$tbody$$", tbody)
        html = html.replace("$$extras$$", extras)
        html = html.replace("$$spans$$", str(spans))
        return html


class SMTPParams:
    def __init__(self, server: str, port: int, sender: str, password: str):
        self.server = server
        self.port = port
        self.sender = sender
        self.password = password


def sendQQMail(title: str, content: str, receiver: str = None, params: SMTPParams = None):
    # 设置SMTP服务器地址和端口
    smtp_server = params.server if params else Env.get("smtp_server")
    port = params.port if params else Env.getInt("smtp_port")  # 对于TLS，通常使用587端口；对于SSL，使用465端口
    sender = params.sender if params else Env.get("smtp_sender")  # 你的电子邮件地址
    password = params.password if params else Env.get("smtp_password")  # 你的电子邮件密码（对于某些电子邮件提供商，你可能需要生成一个应用专用密码）
    receiver = receiver if receiver else Env.get("smtp_receiver")

    if not sender or not password:
        return

    # 创建消息对象
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = title  # 邮件主题
    body = content  # 邮件正文
    message.attach(MIMEText(body, "plain"))

    # 连接到SMTP服务器并发送邮件
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # 启动TLS模式
        server.login(sender, password)  # 登录你的账户
        server.sendmail(sender, receiver, message.as_string())  # 发送邮件
    except Exception as e:
        print(f"Error: unable to send email. {e}")


def sendMail(title: str, content: str | HtmlTableEmail, receiver: str = None, params: SMTPParams = None):
    # 设置SMTP服务器地址和端口
    smtp_server = params.server if params else Env.get("smtp_server")
    port = params.port if params else Env.getInt("smtp_port")  # 对于TLS，通常使用587端口；对于SSL，使用465端口
    sender = params.sender if params else Env.get("smtp_sender")  # 你的电子邮件地址
    password = params.password if params else Env.get("smtp_password")  # 你的电子邮件密码（对于某些电子邮件提供商，你可能需要生成一个应用专用密码）
    receiver = receiver if receiver else Env.get("smtp_receiver")

    if not sender or not password:
        return

    # 创建消息对象
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = title  # 邮件主题
    if isinstance(content, HtmlTableEmail):
        body = content.toHtml()  # 邮件正文
        message.attach(MIMEText(body, "html"))
    else:
        body = content  # 邮件正文
        message.attach(MIMEText(body, "plain"))

    # 连接到SMTP服务器并发送邮件
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # 启动TLS模式
        server.login(sender, password)  # 登录你的账户
        server.sendmail(sender, receiver, message.as_string())  # 发送邮件
    except Exception as e:
        print(f"Error: unable to send email. {e}")
