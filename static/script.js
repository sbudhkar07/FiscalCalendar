document.addEventListener('DOMContentLoaded', function(){ //wait for the DOM to load
    const prevButton = document.getElementById('prev'); //set up access to the previous and next buttons, the selected month and country
    const nextButton = document.getElementById('next');
    const selectedMonth = document.getElementById('selected_month'); 
    const country = document.getElementById('Country')

    const today = new Date(); //initialise a date object to refer to the current month

    let currentYear = today.getFullYear(); //reference the current year, month and selected country
    let currentMonth = today.getMonth() + 1;
    let selectedCountry = country.value;

    async function updateCalendar(year, month, country){
        try {
            const response = await fetch(`/update_calendar?year=${year}&month=${month}&country=${country}`);  //create promise for the data from the url
            const data = await response.json(); //parse the response
        
            selectedMonth.textContent = data.selected_month; //set the text in the header to the month selected by the user
            const monthDiv = document.querySelector('.month'); //get access to the div containing the calendar grid
            monthDiv.innerHTML = ''; //empty the previous month's grid
            data.month.forEach(week => { 
                const weekDiv = document.createElement('div'); //create a div for each week in the month, given by the json data received from Flask
                weekDiv.classList.add('week'); //add the class attribute "week" to the week div
                week.forEach(day => {
                    const dayDiv = document.createElement('div'); //create a div for each day in the week
                    dayDiv.classList.add('day'); //add the class attribute "day" to the day div
                    dayDiv.innerHTML = `
                        <div class="date">${day.day}</div> 
                        <div class="tasks">
                            ${day.tasks.map(task => `<div class="task">${task}</div>`).join('')}
                        </div>
                    `; //add divs for the date and task within the day div
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
        updateCalendar(currentYear, currentMonth, selectedCountry); //update the calendar if the previous button is clicked
    });

    nextButton.addEventListener('click', () => {
        currentMonth += 1;
        if (currentMonth > 12){
            currentMonth = 1;
            currentYear += 1
        }
        updateCalendar(currentYear, currentMonth, selectedCountry) //update the calendar if the next button is clicked
    });

    country.addEventListener('change', () => {
        selectedCountry = country.value;
        updateCalendar(currentYear, currentMonth, selectedCountry);
    });

    updateCalendar(currentYear, currentMonth, selectedCountry); //update the calendar if the country is changed
});