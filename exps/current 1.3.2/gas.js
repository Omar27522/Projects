let currentEntryId = null;

function calculatePPG() {
    var amount = parseFloat(document.getElementById('amount').value) || 0;
    var gallons = parseFloat(document.getElementById('gallons').value) || 0;
    var ppg = gallons > 0 ? (amount / gallons).toFixed(3) : '0.000';
    document.getElementById('ppg').value = ppg;
}

function calculateTanksPerDollarMile(amount, gallons, tankSize) {
    if (amount <= 0 || gallons <= 0 || tankSize <= 0) return '0.000';
    const tanksPerDollarMile = (tankSize / gallons) / amount;
    return tanksPerDollarMile.toFixed(3);
}

function updateTable(entries) {
    const tbody = document.querySelector('table tbody');
    if (!tbody) return;

    tbody.innerHTML = '';
    const tankSize = parseFloat(document.getElementById('tankSize').value) || 18;

    entries.forEach(entry => {
        const tr = document.createElement('tr');
        tr.onclick = () => showEntry(entry);
        
        const tanksPerDollarMile = calculateTanksPerDollarMile(
            parseFloat(entry.amount), 
            parseFloat(entry.gallons),
            tankSize
        );
        
        tr.innerHTML = `
            <td>${entry.date}</td>
            <td>${entry.station}</td>
            <td>${entry.type}</td>
            <td>${entry.amount}</td>
            <td>${entry.gallons}</td>
            <td>${entry.price_per_gallon}</td>
            <td>${tanksPerDollarMile}</td>
        `;
        
        tbody.appendChild(tr);
    });
}

function updateMonthlyStats(entries) {
    const gallonsPerTank = parseFloat(document.getElementById('gallonsPerTank').value) || 18;
    const milesPerTank = parseFloat(document.getElementById('milesPerTank').value) || 370;

    // Filter entries based on selected month and year
    const selectedMonth = document.getElementById('statsMonthFilter').value;
    const selectedYear = document.getElementById('statsYearFilter').value;
    
    const filteredEntries = entries.filter(entry => {
        const entryDate = new Date(entry.date);
        return (!selectedMonth || entryDate.getMonth() + 1 === parseInt(selectedMonth)) &&
               (!selectedYear || entryDate.getFullYear() === parseInt(selectedYear));
    });

    let totalGallons = 0;
    let totalAmount = 0;
    let totalMiles = 0;

    filteredEntries.forEach(entry => {
        const gallons = parseFloat(entry.gallons) || 0;
        const amount = parseFloat(entry.amount) || 0;
        
        totalGallons += gallons;
        totalAmount += amount;
        totalMiles += (gallons / gallonsPerTank) * milesPerTank;
    });

    const avgPricePerGallon = totalGallons > 0 ? totalAmount / totalGallons : 0;
    const tanksUsed = totalGallons / gallonsPerTank;

    // Update the stats table
    document.getElementById('gasPerMonth').textContent = totalGallons.toFixed(3);
    document.getElementById('dollarsPerMonth').textContent = '$' + totalAmount.toFixed(2);
    document.getElementById('avgPricePerGallon').textContent = '$' + avgPricePerGallon.toFixed(3);
    document.getElementById('milesTraveled').textContent = Math.round(totalMiles);
    document.getElementById('tanksUsed').textContent = tanksUsed.toFixed(2);
}

function filterEntries() {
    const year = document.getElementById('yearFilter').value;
    const month = document.getElementById('monthFilter').value;
    
    const formData = new FormData();
    formData.append('filter_year', year);
    formData.append('filter_month', month);
    formData.append('action', 'filter');

    fetch(window.location.href, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateTable(data.entries);
            updateMonthlyStats(data.entries);
        } else {
            alert(data.message || 'Error filtering entries');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while filtering entries');
    });
}

function resetFilter() {
    document.getElementById('yearFilter').value = '';
    document.getElementById('monthFilter').value = '';
    filterEntries();
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('applyFilter').addEventListener('click', filterEntries);
    document.getElementById('resetFilter').addEventListener('click', resetFilter);
    
    // Add listeners for stats filters and inputs
    document.getElementById('statsMonthFilter').addEventListener('change', () => {
        document.getElementById('monthFilter').value = '';  // Clear main filter
        filterEntries();
    });
    
    document.getElementById('statsYearFilter').addEventListener('change', () => {
        document.getElementById('yearFilter').value = '';  // Clear main filter
        filterEntries();
    });
    
    // Tank size and miles per tank listeners
    ['gallonsPerTank', 'milesPerTank'].forEach(id => {
        document.getElementById(id).addEventListener('input', () => {
            const entries = Array.from(document.querySelectorAll('table:not(.stats-table) tbody tr')).map(row => ({
                date: row.cells[0].textContent,
                gallons: parseFloat(row.cells[4].textContent),
                amount: parseFloat(row.cells[3].textContent)
            }));
            updateMonthlyStats(entries);
        });
    });
});

function showEntry(entry) {
    currentEntryId = entry.id;
    document.getElementById('modalDate').textContent = entry.date;
    document.getElementById('modalStation').textContent = entry.station;
    document.getElementById('modalType').textContent = entry.type;
    document.getElementById('modalAmount').textContent = entry.amount;
    document.getElementById('modalGallons').textContent = entry.gallons;
    document.getElementById('modalPPG').textContent = entry.price_per_gallon;
    document.getElementById('entryModal').style.display = 'block';
}

function deleteEntry() {
    if (currentEntryId && confirm('Are you sure you want to delete this entry?')) {
        const formData = new FormData();
        formData.append('delete_id', currentEntryId);

        fetch(window.location.href, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                closeModal();
                location.reload(); // Temporary reload until we implement updateTable
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the entry');
        });
    }
}

function editEntry() {
    if (currentEntryId) {
        document.getElementById('entry_id').value = currentEntryId;
        document.getElementById('date').value = document.getElementById('modalDate').textContent;
        document.getElementById('station').value = document.getElementById('modalStation').textContent;
        document.getElementById('type').value = document.getElementById('modalType').textContent;
        document.getElementById('amount').value = document.getElementById('modalAmount').textContent;
        document.getElementById('gallons').value = document.getElementById('modalGallons').textContent;
        document.getElementById('ppg').value = document.getElementById('modalPPG').textContent;
        
        closeModal();
        document.getElementById('gasForm').scrollIntoView({ behavior: 'smooth' });
    }
}

function closeModal() {
    document.getElementById('entryModal').style.display = 'none';
    currentEntryId = null;
}

function addNewStation() {
    var newStation = document.getElementById('newStation').value;
    if (newStation.trim() !== '') {
        var select = document.getElementById('station');
        var option = document.createElement('option');
        option.value = newStation;
        option.text = newStation;
        select.insertBefore(option, select.lastElementChild);
        select.value = newStation;
        document.getElementById('newStationDiv').style.display = 'none';
        document.getElementById('newStation').value = '';
    }
}

function removeStation() {
    var select = document.getElementById('station');
    var selectedOption = select.options[select.selectedIndex];
    
    if (selectedOption.value !== '' && 
        selectedOption.value !== 'other' && 
        confirm('Remove station: ' + selectedOption.text + '?')) {
        select.remove(select.selectedIndex);
        select.value = ''; // Reset to "Select Station"
    }
}

document.getElementById('gasForm').onsubmit = function(e) {
    e.preventDefault();
    const formData = new FormData(this);

    fetch(window.location.href, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Clear form
            this.reset();
            document.getElementById('entry_id').value = '';
            // Update table with new data
            updateTable(data.entries);
            // Show success message
            alert(data.message);
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while saving the entry');
    });
};