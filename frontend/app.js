const agentSelect = document.getElementById("agent");
const promptInput = document.getElementById("prompt");
const responseBox = document.getElementById("response");
const sendBtn = document.getElementById("sendBtn");

async function enviarPrompt() {
    const agent = agentSelect.value;
    const prompt = promptInput.value.trim();

    if (!prompt) {
        responseBox.textContent = "Escribe un prompt primero.";
        return;
    }

    responseBox.textContent = "Pensando...";
    sendBtn.disabled = true;

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                agent: agent,
                prompt: prompt
            })
        });

        const data = await res.json();

        if (data.answer) {
            responseBox.textContent = data.answer;
        } else {
            responseBox.textContent = JSON.stringify(data, null, 2);
        }
    } catch (error) {
        responseBox.textContent = "Error: " + error;
    } finally {
        sendBtn.disabled = false;
    }
}

sendBtn.addEventListener("click", enviarPrompt);

promptInput.addEventListener("keydown", function (event) {
    if (event.ctrlKey && event.key === "Enter") {
        enviarPrompt();
    }
});
