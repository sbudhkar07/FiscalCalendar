document.addEventListener("DOMContentLoaded", () => {
    const moreDates = document.getElementById("add_more");
    const dateContainer = document.getElementById("date_container")

    moreDates.addEventListener("click", () => {
        const dateDiv = document.createElement("div");
        dateDiv.className = "date_select";

        const dateInput = document.createElement("input");
        dateInput.type = "date";
        dateInput.name = "date[]";

        dateDiv.appendChild(dateInput);
        dateContainer.appendChild(dateDiv);
    });
});