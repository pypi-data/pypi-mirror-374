from pybase.pusher import SMTPParams, sendMail, HtmlTableEmail

if __name__ == "__main__":
    params = SMTPParams("smtp.qq.com", 587, "2328697997@qq.com", "tbivvqolbinoecij")
    table = HtmlTableEmail("Pupu", ["备注", "朴分", "红包"])
    table.rows.append(["测试", "100", "3.54"])
    table.rows.append(["测试", "100", "3.54"])
    table.rows.append(["测试", "100", "3.54"])
    table.extras.append("tbivvqolbinoecij")
    table.extras.append("tbivvqolbinoecij")
    sendMail("测试邮件", table, receiver="2292487535@qq.com", params=params)
