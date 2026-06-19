const formArea = document.getElementById("form-area");
const resultArea = document.getElementById("result-area");
const loader = document.querySelector(".loading-ring");

document.getElementById("form").addEventListener("submit", async function(e) {
    e.preventDefault();
    
    const errorBox = document.getElementById("error-message");
    formArea.style.display = "none";
    loader.style.display = "flex";

    const formData = {
        id: document.querySelector("[name='id']").value,
        password: document.querySelector("[name='password']").value,
        year: document.querySelector("[name='year']").value,
        month: document.querySelector("[name='month']").value
    };
    //const year = Number(formData.year);
    const yearInput = document.querySelector("[name='year']");
    const year = Number(yearInput.value);

    //const month = Number(formData.month);
    const monthInput = document.querySelector("[name='month']");
    const month = Number(monthInput.value);

    if(Number.isNaN(year)){
        yearInput.value = "";
        errorBox.textContent = "年は数字で入力してください"
        yearInput.placeholder = "年は数字で入力してください";
        formArea.style.display = "block";
        resultArea.style.display = "none";
        loader.style.display = "none";
        return;
    }

    if(Number.isNaN(month)){
        monthInput.value = "";
        errorBox.textContent = "月は数字で入力してください";
        monthInput.placeholder = "月は数字で入力してください";
        formArea.style.display = "block";
        resultArea.style.display = "none";
        loader.style.display = "none";
        return;
    }

    if(month < 1 || month > 12){
        monthInput.value = "";
        errorBox.textContent = "月は1～12で入力してください";
        monthInput.placeholder = "月は1～12で入力してください"
        formArea.style.display = "block";
        resultArea.style.display = "none";
        loader.style.display = "none";
        return;
    }


    const res = await fetch("/calc", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)
    });

    if (!res.ok) {
    const err = await res.json();

    errorBox.textContent = "ログイン失敗";
    
    resultArea.style.display = "none";
    loader.style.display = "none";
    formArea.style.display = "block";

    window.history.back();


    return;
}
    const data = await res.json();

    document.querySelector(".loading-ring").style.display = "none";

    document.getElementById("result").innerHTML = `
        <h2>給与：${data.salary}円</h2>
        <hr>
        高校生：${data.high}コマ<br>
        中学生：${data.junior}コマ<br>
        小学生：${data.elementaly}コマ<br>
        3加算：${data.three}コマ<br>
        2加算：${data.two}コマ<br>
    `;

    resultArea.style.display = "block";
});

document.getElementById("backBtn").addEventListener("click", function() {
    resultArea.style.display = "none";
    formArea.style.display = "block";
});