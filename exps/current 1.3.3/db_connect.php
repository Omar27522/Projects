<?php
class Database {
    private $db;

    public function __construct() {
        try {
            // Get the absolute path to the database file
            $rootDir = dirname(__FILE__);
            $dbPath = $rootDir . '/expenses.db';
            $this->db = new PDO('sqlite:' . $dbPath);
            $this->db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            $this->createTable();//expenses table
            $this->createGasTable();//gas table
            $this->createStationsTable();//stations table
        } catch (PDOException $e) {
            echo "Error connecting to database: " . $e->getMessage();
        }
    }

    private function createTable() {
        $query = "CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            item TEXT NOT NULL,
            place TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )";

        $this->db->exec($query);
    }

    private function createGasTable() {
        $this->db->exec("CREATE TABLE IF NOT EXISTS gas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            year INTEGER NOT NULL,
            station TEXT NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            gallons REAL NOT NULL,
            price_per_gallon REAL NOT NULL
        )");
    }

    private function createStationsTable() {
        try {
            $this->db->exec("CREATE TABLE IF NOT EXISTS stations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )");
            
            // Check if table is empty and add default stations
            $count = $this->db->query("SELECT COUNT(*) FROM stations")->fetchColumn();
            if ($count == 0) {
                $defaultStations = ['Shell', 'BP', 'Chevron'];
                $stmt = $this->db->prepare("INSERT INTO stations (name) VALUES (:name)");
                foreach ($defaultStations as $station) {
                    $stmt->execute([':name' => $station]);
                }
            }
        } catch (PDOException $e) {
            echo "Error creating stations table: " . $e->getMessage();
        }
    }

    public function addExpense($date, $item, $place, $amount, $type) {
        $query = $this->db->prepare('INSERT INTO expenses (date, item, place, amount, type) VALUES (:date, :item, :place, :amount, :type)');
        $query->bindValue(':date', $date, PDO::PARAM_STR);
        $query->bindValue(':item', $item, PDO::PARAM_STR);
        $query->bindValue(':place', $place, PDO::PARAM_STR);
        $query->bindValue(':amount', $amount, PDO::PARAM_STR);
        $query->bindValue(':type', $type, PDO::PARAM_STR);
        return $query->execute();
    }

    public function getAllExpenses() {
        $query = "SELECT id, date, item, place, amount, type,
                  strftime('%Y', date) as year,
                  strftime('%m', date) as month,
                  strftime('%d', date) as day
                  FROM expenses
                  ORDER BY date DESC";
        $stmt = $this->db->query($query);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getMonthlyExpenses() {
        $query = "SELECT strftime('%Y-%m', date) as month,
                  date, item, place, amount, type
                  FROM expenses
                  ORDER BY date DESC";
        $stmt = $this->db->query($query);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getExpenseById($id) {
        $query = $this->db->prepare('SELECT * FROM expenses WHERE id = :id');
        $query->bindValue(':id', $id, PDO::PARAM_INT);
        $query->execute();
        return $query->fetch(PDO::FETCH_ASSOC);
    }

    public function updateExpense($id, $date, $item, $place, $amount, $type) {
        $query = $this->db->prepare('UPDATE expenses SET date = :date, item = :item, place = :place, amount = :amount, type = :type WHERE id = :id');
        $query->bindValue(':id', $id, PDO::PARAM_INT);
        $query->bindValue(':date', $date, PDO::PARAM_STR);
        $query->bindValue(':item', $item, PDO::PARAM_STR);
        $query->bindValue(':place', $place, PDO::PARAM_STR);
        $query->bindValue(':amount', $amount, PDO::PARAM_STR);
        $query->bindValue(':type', $type, PDO::PARAM_STR);
        return $query->execute();
    }

    public function deleteExpense($id) {
        $query = $this->db->prepare('DELETE FROM expenses WHERE id = :id');
        $query->bindValue(':id', $id, PDO::PARAM_INT);
        return $query->execute();
    }

    public function addGasEntry($date, $station, $type, $amount, $gallons, $price_per_gallon) {
        $year = date('Y', strtotime($date));
        $query = $this->db->prepare('INSERT INTO gas (date, year, station, type, amount, gallons, price_per_gallon) 
                                   VALUES (:date, :year, :station, :type, :amount, :gallons, :price_per_gallon)');
        try {
            $query->bindValue(':date', $date, PDO::PARAM_STR);
            $query->bindValue(':year', $year, PDO::PARAM_INT);
            $query->bindValue(':station', $station, PDO::PARAM_STR);
            $query->bindValue(':type', $type, PDO::PARAM_STR);
            $query->bindValue(':amount', $amount, PDO::PARAM_STR);
            $query->bindValue(':gallons', $gallons, PDO::PARAM_STR);
            $query->bindValue(':price_per_gallon', $price_per_gallon, PDO::PARAM_STR);
            $query->execute();
            return true;
        } catch (PDOException $e) {
            echo "Error: " . $e->getMessage();
            return false;
        }
    }

    public function getDistinctTypes() {
        $query = "SELECT DISTINCT type FROM expenses ORDER BY type ASC";
        $stmt = $this->db->query($query);
        $types = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $types[] = $row['type'];
        }
        return $types;
    }

    public function getDistinctYears() {
        $query = "SELECT DISTINCT strftime('%Y', date) as year FROM expenses ORDER BY year DESC";
        $stmt = $this->db->query($query);
        $years = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $years[] = $row['year'];
        }
        return $years;
    }

    public function getExpensesByMonth($month, $type = null) {
        $months = array(
            1 => 'Jan', 2 => 'Feb', 3 => 'Mar', 4 => 'Apr',
            5 => 'May', 6 => 'Jun', 7 => 'Jul', 8 => 'Aug',
            9 => 'Sep', 10 => 'Oct', 11 => 'Nov', 12 => 'Dec'
        );

        $monthStr = $months[$month];
        $sql = "SELECT * FROM expenses WHERE date LIKE :monthPattern";
        if ($type) {
            $sql .= " AND type = :type";
        }
        $sql .= " ORDER BY date DESC";

        $query = $this->db->prepare($sql);
        $query->bindValue(':monthPattern', $monthStr . '-%', PDO::PARAM_STR);
        if ($type) {
            $query->bindValue(':type', $type, PDO::PARAM_STR);
        }

        $query->execute();
        return $query->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getExpensesByMonthYear($month, $year) {
        $query = "SELECT * FROM expenses
                 WHERE date LIKE :yearMonth || '%'
                 ORDER BY date DESC";
        try {
            $stmt = $this->db->prepare($query);
            $yearMonth = $year . '-' . str_pad($month, 2, '0', STR_PAD_LEFT);
            $stmt->bindValue(':yearMonth', $yearMonth, PDO::PARAM_STR);
            $stmt->execute();
            return $stmt->fetchAll(PDO::FETCH_ASSOC);
        } catch (PDOException $e) {
            echo "Error: " . $e->getMessage();
            return null;
        }
    }

    public function getYearlyExpenses() {
        $query = "SELECT id, date, item, place, amount, type FROM expenses ORDER BY date DESC";
        $stmt = $this->db->query($query);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getYearlyExpensesSummary() {
        $query = "SELECT strftime('%Y', date) as year,
                  SUM(amount) as total_amount,
                  COUNT(*) as transaction_count
                  FROM expenses
                  GROUP BY year
                  ORDER BY year DESC";
        $stmt = $this->db->query($query);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getMonthlyExpensesSummary() {
        $query = "SELECT strftime('%Y-%m', date) as month,
                  SUM(amount) as total_amount,
                  COUNT(*) as transaction_count
                  FROM expenses
                  GROUP BY month
                  ORDER BY month DESC";
        $stmt = $this->db->query($query);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getExpensesByYear($year) {
        $query = $this->db->prepare('SELECT * FROM expenses WHERE strftime("%Y", date) = :year ORDER BY date DESC');
        $query->bindValue(':year', $year, PDO::PARAM_STR);
        $query->execute();
        return $query->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getAllGasEntries() {
        $query = "SELECT id, date, station, type, amount, gallons, price_per_gallon FROM gas ORDER BY date DESC";
        try {
            $stmt = $this->db->query($query);
            $entries = $stmt->fetchAll(PDO::FETCH_ASSOC);
            return $entries;
        } catch (PDOException $e) {
            echo "Error: " . $e->getMessage();
            return [];
        }
    }

    public function deleteGasEntry($id) {
        $query = $this->db->prepare('DELETE FROM gas WHERE id = :id');
        $query->bindValue(':id', $id, PDO::PARAM_INT);
        return $query->execute();
    }

    public function updateGasEntry($id, $date, $station, $type, $amount, $gallons, $ppg) {
        $year = date('Y', strtotime($date));
        $query = "UPDATE gas SET 
                 date = :date,
                 year = :year,
                 station = :station,
                 type = :type,
                 amount = :amount,
                 gallons = :gallons,
                 price_per_gallon = :ppg
                 WHERE id = :id";
        try {
            $stmt = $this->db->prepare($query);
            $stmt->bindValue(':id', $id, PDO::PARAM_INT);
            $stmt->bindValue(':date', $date, PDO::PARAM_STR);
            $stmt->bindValue(':year', $year, PDO::PARAM_INT);
            $stmt->bindValue(':station', $station, PDO::PARAM_STR);
            $stmt->bindValue(':type', $type, PDO::PARAM_STR);
            $stmt->bindValue(':amount', $amount, PDO::PARAM_STR);
            $stmt->bindValue(':gallons', $gallons, PDO::PARAM_STR);
            $stmt->bindValue(':ppg', $ppg, PDO::PARAM_STR);
            return $stmt->execute();
        } catch (PDOException $e) {
            echo "Error: " . $e->getMessage();
            return false;
        }
    }

    public function getFilteredEntries($year = null, $month = null) {
        $query = "SELECT * FROM gas WHERE 1=1";
        $params = [];

        if ($year) {
            $query .= " AND year = ?";
            $params[] = $year;
        }

        if ($month) {
            // Create a mapping of month numbers to their abbreviations
            $monthAbbreviations = [
                1 => 'Jan', 2 => 'Feb', 3 => 'Mar', 4 => 'Apr',
                5 => 'May', 6 => 'Jun', 7 => 'Jul', 8 => 'Aug',
                9 => 'Sep', 10 => 'Oct', 11 => 'Nov', 12 => 'Dec'
            ];

            // If month is provided as a number, get its abbreviation
            $monthAbbr = $monthAbbreviations[(int)$month];
            $query .= " AND date LIKE ?";
            $params[] = $monthAbbr . " %";
        }

        $query .= " ORDER BY date DESC";

        try {
            $stmt = $this->db->prepare($query);
            if (!empty($params)) {
                $stmt->execute($params);
            } else {
                $stmt->execute();
            }
            return $stmt->fetchAll(PDO::FETCH_ASSOC);
        } catch (PDOException $e) {
            error_log("Error filtering entries: " . $e->getMessage());
            return false;
        }
    }

    public function getGasEntryById($id) {
        $query = "SELECT * FROM gas WHERE id = :id";
        try {
            $stmt = $this->db->prepare($query);
            $stmt->bindValue(':id', $id, PDO::PARAM_INT);
            $stmt->execute();
            return $stmt->fetch(PDO::FETCH_ASSOC);
        } catch (PDOException $e) {
            echo "Error: " . $e->getMessage();
            return null;
        }
    }

    public function getAllStations() {
        try {
            $query = "SELECT name FROM stations ORDER BY name ASC";
            $stmt = $this->db->query($query);
            return $stmt->fetchAll(PDO::FETCH_COLUMN);
        } catch (PDOException $e) {
            error_log("Error getting stations: " . $e->getMessage());
            return [];
        }
    }

    public function addStation($name) {
        try {
            $query = $this->db->prepare('INSERT INTO stations (name) VALUES (:name)');
            $query->bindValue(':name', $name, PDO::PARAM_STR);
            return $query->execute();
        } catch (PDOException $e) {
            error_log("Error adding station: " . $e->getMessage());
            return false;
        }
    }

    public function deleteStation($name) {
        try {
            $query = $this->db->prepare('DELETE FROM stations WHERE name = :name');
            $query->bindValue(':name', $name, PDO::PARAM_STR);
            return $query->execute();
        } catch (PDOException $e) {
            error_log("Error deleting station: " . $e->getMessage());
            return false;
        }
    }
}

function links () {
    echo '<div class="crumbs">
        <a href="../monthly/">Monthly Expenses</a>
        <a href="../gas">GAS</a>
        <a href="#Budget">Budget</a>
        <a href="#tips">tips</a>
        <a href="#LAPC">LAPC</a>
        <a href="../bank/">Bank</a>
        </div>';
}
function footer () {
    echo '<div class="footer">
        <a href="../monthly/">Monthly Expenses</a>
        <a href="../gas">GAS</a>
        <a href="#Budget">Budget</a>
        <a href="#tips">tips</a>
        <a href="#LAPC">LAPC</a>
        <a href="../bank/">Bank</a>
        </div>';
}
?>