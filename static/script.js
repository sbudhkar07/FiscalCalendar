document.addEventListener('DOMContentLoaded', function(){ //wait for the DOM to load
    const prevButton = document.getElementById('prev'); //set up access to the previous and next buttons
    const nextButton = document.getElementById('next');
    const selectedMonth = document.getElementById('selected_month'); 
    const country = document.getElementById('Country')

    const today = new Date();

    let currentYear = today.getFullYear();
    let currentMonth = today.getMonth() + 1;
    let selectedCountry = country.value;

    async function updateCalendar(year, month, country){
        try {
            const response = await fetch(`/update_calendar?year=${year}&month=${month}&country=${country}`);
            const data = await response.json();
        
            selectedMonth.textContent = data.selected_month;
            const monthDiv = document.querySelector('.month');
            monthDiv.innerHTML = '';
            data.month.forEach(week => {
                const weekDiv = document.createElement('div');
                weekDiv.classList.add('week');
                week.forEach(day => {
                    const dayDiv = document.createElement('div');
                    dayDiv.classList.add('day');
                    dayDiv.innerHTML = `
                        <div class="date">${day.day}</div>
                        <div class="tasks">
                            ${day.tasks.map(task => `<div class="task">${task}</div>`).join('')}
                        </div>
                    `;
                    weekDiv.appendChild(dayDiv);
                });
                monthDiv.appendChild(weekDiv);
            });
        } catch (error) {
            console.error("Error fetching calendar data:", error);
        }
    };
        

    prevButton.addEventListener('click', () => {
        currentMonth -= 1;
        if (currentMonth < 1){
            currentMonth = 12;
            currentYear -= 1
        }
        updateCalendar(currentYear, currentMonth, selectedCountry);
    });

    nextButton.addEventListener('click', () => {
        currentMonth += 1;
        if (currentMonth > 12){
            currentMonth = 1;
            currentYear += 1
        }
        updateCalendar(currentYear, currentMonth, selectedCountry)
    });

    country.addEventListener('change', () => {
        selectedCountry = country.value;
        updateCalendar(currentYear, currentMonth, selectedCountry);
    });

    updateCalendar(currentYear, currentMonth, selectedCountry);
});