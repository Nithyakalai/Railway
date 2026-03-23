function searchTrains() {
    const data = {
        from: document.getElementById("from").value,
        to: document.getElementById("to").value,
        date: document.getElementById("date").value
    };

    if (!data.from || !data.to || !data.date) {
        alert("Please select From station, To station, and Date");
        return;
    }

    fetch('/search_trains', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(trains => {
        const card = document.getElementById("resultsCard");
        const tbody = document.querySelector("#results tbody");
        const noResults = document.getElementById("noResults");
        const table = document.getElementById("results");

        card.style.display = "block";
        tbody.innerHTML = "";

        if (trains.length === 0) {
            table.style.display = "none";
            noResults.style.display = "block";
            return;
        }

        table.style.display = "table";
        noResults.style.display = "none";

        trains.forEach(t => {
            const row = `
            <tr>
                <td><span class="badge badge-blue">${t.train_no}</span></td>
                <td>${t.train_name}</td>
                <td>${t.from_station}</td>
                <td>${t.to_station}</td>
                <td>${t.departure_time || '-'}</td>
                <td>${t.arrival_time || '-'}</td>
                <td>${t.boarding_date}</td>
                <td>${t.available_seats}</td>
                <td><input type="number" min="1" max="${t.available_seats}" value="1" id="seat_${t.train_no}"></td>
                <td><button class="btn-sm" onclick="book('${t.train_no}')">Book</button></td>
            </tr>`;
            tbody.innerHTML += row;
        });
    });
}

function book(train_no) {
    const seats = document.getElementById(`seat_${train_no}`).value;

    if (!seats || seats < 1) {
        alert("Please enter number of seats");
        return;
    }

    const data = {
        train_no: train_no,
        date: document.getElementById("date").value,
        from: document.getElementById("from").value,
        to: document.getElementById("to").value,
        seats: seats
    };

    fetch('/book_ticket', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(res => {
        alert(res.status);
        if (res.status.includes("✅")) {
            location.reload();
        }
    });
}
