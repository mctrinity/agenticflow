function fillText(text) {
    document.querySelector("textarea[name='text']").value = text;
}

document.addEventListener("DOMContentLoaded", () => {
    const summaryDiv = document.getElementById("summary");

    async function refreshSummary() {
        try {
            if (!summaryDiv) return;
            summaryDiv.classList.add("updating");
            const res = await fetch("/summary");
            const html = await res.text();
            summaryDiv.innerHTML = html;
        } catch (err) {
            console.error("Summary update failed:", err);
        } finally {
            summaryDiv.classList.remove("updating");
        }
    }

    // Load summary immediately when page loads
    refreshSummary();

    // Refresh every 10 seconds
    setInterval(refreshSummary, 10000);
});

function clearInput() {
  const textarea = document.querySelector("textarea[name='text']");
  textarea.value = "";
  textarea.focus();
}
