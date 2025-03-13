function showUpload() {
    document.getElementById('upload-form').style.display = 'block';
    document.getElementById('manual-form').style.display = 'none';
}

function showManual() {
    document.getElementById('upload-form').style.display = 'none';
    document.getElementById('manual-form').style.display = 'block';
}

document.getElementById('upload-form').onsubmit = async function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    try {
        const response = await fetch('https://alzimer-demo.onrender.com/upload', {  // ✅ แก้ URL
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        document.getElementById('result').innerHTML = `<p>Prediction results: ${result.predictions.map(pred => pred === 1 ? 'Positive' : 'Negative').join(', ')}</p>`;
    } catch (error) {
        document.getElementById('result').innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    }
}

document.getElementById('manual-form').onsubmit = async function (e) {
    e.preventDefault();

    const field1 = document.querySelector('input[name="field1"]').value;
    const field2 = document.querySelector('input[name="field2"]').value;
    const field3 = document.querySelector('input[name="field3"]').value;
    const field4 = document.querySelector('input[name="field4"]').value;
    const field5 = document.querySelector('input[name="field5"]').value;

    console.log("Sending data:", { field1, field2, field3, field4, field5 });

    if (!field1 || isNaN(field1) || parseFloat(field1) < 0) {
        alert("Please enter a valid MMSE Score (float).");
        return;
    }

    if (!field2 || isNaN(field2) || parseFloat(field2) < 0) {
        alert("Please enter a valid FunctionalAssessment Score (float).");
        return;
    }

    if (!field5 || isNaN(field5) || parseFloat(field5) < 0) {
        alert("Please enter a valid ADL (float).");
        return;
    }

    if (field3 === "" || field4 === "") {
        alert("Please select values for Memory Complaints and Behavioral Problems.");
        return;
    }

    const formData = new FormData();
    formData.append("field1", field1);
    formData.append("field2", field2);
    formData.append("field3", field3);
    formData.append("field4", field4);
    formData.append("field5", field5);

    try {
        const response = await fetch('https://alzimer-demo.onrender.com/manual', {  // ✅ แก้ URL
            method: 'POST',
            body: formData
        });
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = await response.json();
        document.getElementById('result').innerHTML = `<p>Prediction results: ${result.predictions.map(pred => pred === 1 ? 'Positive' : 'Negative').join(', ')}</p>`;
    } catch (error) {
        document.getElementById('result').innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    }
};

function predictAgain() {
    document.getElementById("result").innerHTML = "";
    document.getElementById("upload-form").reset();
    document.getElementById("manual-form").reset();
    document.getElementById("upload-form").style.display = "block";
    document.getElementById("manual-form").style.display = "none";
}

function toggleShadow() {
    const form = document.querySelector('.quote-form');
    form.classList.toggle('shadow-effect');
}

function setValue(fieldId, value, groupId) {
    document.getElementById(fieldId).value = value;
    let buttons = document.querySelectorAll(`#${groupId} button`);
    buttons.forEach(btn => btn.classList.remove("selected"));
    buttons[value].classList.add("selected");
}
