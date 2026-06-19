from playwright.sync_api import sync_playwright, TimeoutError
from flask import Flask, render_template, request, jsonify

#現在の年月日取得

def get_shift_data(login_ID, login_PASS, target_year, target_month):
    #現在の年月日取得
    def get_year_month(page):
        label = page.locator('.MuiPickersCalendarHeader-label').text_content().strip()
        y, m = label.replace("年", "").replace("月", "").split()
        return int(y), int(m)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)         #headlessをFalseにすると画面表示
        page = browser.new_page()
        page.goto("URL")
        page.get_by_label("ID").fill(str(login_ID))
        page.get_by_label("パスワード").fill(str(login_PASS))
        page.get_by_role("button", name="ログイン").click(force=True)
        try:
            # ログイン成功待ち
            page.wait_for_url("**/home", timeout=3000)
        except TimeoutError:
            print("ログイン失敗 or 遷移しませんでした")
            return None

        page.goto("URL")
        
        #検索したい年,月
        month = {'1':31, '2':28, '3':31, '4':30, '5':31, '6':30, '7':31, '8':31, '9':30, '10':31, '11':30, '12':31}
        
        #**********************************期間開始**********************************#
        page.locator('label:has-text("期間:開始")').locator("xpath=..").click()
        page.locator('.MuiPickersCalendarHeader-label').click();
        page.get_by_role("radio", name=str(target_year)).click()            #年の選択
        current_year, current_month = get_year_month(page)
        #月の選択
        if int(target_month) > int(current_month):
            while(int(target_month) != int(current_month)):
                #page.wait_for_selector("text=期間")
                page.get_by_label("次月を表示").click()
                current_year, current_month = get_year_month(page)
                print(current_year)
                print(target_month)
                print(current_month)
        elif int(target_month) < int(current_month):
            while(int(target_month) != int(current_month)):
                #page.wait_for_selector("text=期間")
                page.get_by_label("前月を表示").click()
                current_year, current_month = get_year_month(page)
        #日にちの選択
        page.locator("button[role='gridcell']:has-text('1')").first.click()
        page.get_by_role("button", name="OK").click()

        #**********************************期間終了**********************************#
        page.locator('label:has-text("期間:終了")').locator("xpath=..").click()
        page.locator('.MuiPickersCalendarHeader-label').click();
        page.get_by_role("radio", name=str(target_year)).click()            #年の選択
        current_year, current_month = get_year_month(page)
        #月の選択
        if int(target_month) > int(current_month):
            while(int(target_month) != int(current_month)):
                #page.wait_for_selector("text=期間")
                page.get_by_label("次月を表示").click()
                current_year, current_month = get_year_month(page)
        elif int(target_month) < int(current_month):
            while(int(target_month) != int(current_month)):
                #page.wait_for_selector("text=期間")
                page.get_by_label("前月を表示").click()
                current_year, current_month = get_year_month(page)

        #日にちの選択
        if((int(target_year) - 2024) % 4 == 0):
            month['2'] = 29
        end_day = month[str(target_month)]
        page.locator(f"button[role='gridcell']:has-text('{end_day}')").first.click()
        page.get_by_role("button", name="OK").click()


        page.get_by_role("button", name="検索").click()
        page.wait_for_selector("text=ロード", state="hidden")
        cells = page.locator("td").all_text_contents()

        i = 0
        list_minute = []
        list_time = []
        list_day = []
        list_grade = []
        
        #HTMLからデータの取り出し
        for cell in cells:
            #print(cell)            #抜き出しデータ確認用
            if(i % 8 == 0):
                list_day.append(cell)
            elif(i % 8 == 2):
                time_part = cell.split("(")[0]
                minute_part = cell.split("(")[1].split(")")[0]
                list_time.append(time_part)
                list_minute.append(minute_part)
            elif(i % 8 == 4):
                list_grade.append(cell)
            i += 1
        browser.close()
    return list_day, list_time, list_minute, list_grade
    
def get_salary(list_day, list_time, list_minute ,list_grade):
    #グループ内の要素（高＞中＞小で一番高いやつ１つ）
    def judge(group):
        if group == []:
            return None
        
        if any("高" in g for g in group):
            return "高"
        elif any("中" in g for g in group):
            return "中"
        else:
            return "小"
    #シフト時間>必要なら要素追加
    list_shift = ['16:00～', '17:00～', '18:00～', '19:00～', '20:00～', '21:00～', '22:00～']
    list_count = []
    new_minute = []
    new_time = []
    new_day= []
    new_grade = []

    #指定なしを50分に
    j = 0
    while(j < len(list_minute)):
        if (list_minute[j] == '指定なし'):
            list_minute[j] = '50分'
        j += 1

    j = 0
    while(j < len(list_minute)):
        #グループ開始
        base_time = list_time[j]
        base_day = list_day[j]
    #同じ時間の塊を全部取る
        group_idx = []
        while j < len(list_minute) and list_time[j] == base_time and base_day == list_day[j]:
            group_idx.append(j)
            j += 1

    #前半
        for i in group_idx:
            new_minute.append('50分')
            new_day.append(list_day[i])
            new_grade.append(list_grade[i])
            new_time.append(base_time)

    #後半
        for i in group_idx:
            if list_minute[i] == '100分':
                next_time = list_shift[list_shift.index(base_time)+1]
                new_minute.append('50分')
                new_day.append(list_day[i])
                new_grade.append(list_grade[i])
                new_time.append(next_time)

    count = 1
        
    #加算人数の抜き出し（次の要素と時間と日付が同じならcountに+1）
    for k in range(len(new_day) - 1):
        if (new_day[k] == new_day[k + 1] and new_time[k] == new_time[k + 1]):
            count += 1
        else:
            list_count.append(count)
            count = 1
    list_count.append(count)

    l = 0
    gr_index = 0
    results = []
    #人数リストをもとにグループ分け
    while l < len(list_count):
        v = list_count[l]
        group = new_grade[gr_index:gr_index+v]
        results.append(judge(group))
        gr_index += v
        l += 1
        
    salary = 0

    #時給の入力
    salary_rate = {"高校生":1480, "中学生":1230, "小学生":1170, "３加算":100,"２加算":50}
    
    high = results.count('高')
    junior = results.count('中')
    elementaly = results.count('小')
    three = list_count.count(3)
    two = list_count.count(2)

    salary = salary_rate["高校生"]*high + salary_rate["中学生"]*junior + salary_rate["小学生"]*elementaly + salary_rate["３加算"]*three + salary_rate["２加算"]*two

    print("高校生：{}".format(high))
    print("中学生：{}".format(junior))
    print("小学生：{}".format(elementaly))
    print("３加算：{}".format(three))
    print("２加算：{}".format(two))
    print("給与：{}".format(salary))
    
    return high, junior, elementaly, three, two, salary

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calc", methods=["POST"])
def calc():
    high = junior = elementaly = three = two = salary = None
    user_id = request.json["id"]
    password = request.json["password"]
    year = request.json["year"]
    month = request.json["month"]
    login_check = get_shift_data(str(user_id), str(password), str(year), str(month))
    if login_check is None:
        return jsonify({"error": "invalid login"}), 401
    day, time, minute, grade = login_check
    high, junior, elementaly, three, two, salary = get_salary(day, time, minute, grade)
    return jsonify({"high":high, "junior":junior, "elementaly":elementaly, "three":three, "two":two, "salary":salary})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
