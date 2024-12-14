<?php
class Database {
    private $db;

    public function __construct() {
        try {
            $this->db = new PDO('sqlite:expenses.db');
            $this->db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            $this->createTable();
            $this->createGasTable();
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
        $query = "CREATE TABLE IF NOT EXISTS gas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            station TEXT NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            gallons REAL NOT NULL,
            price_per_gallon REAL NOT NULL
        )";
        
        $this->db->exec($query);
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

    public function insertGasEntry($date, $station, $type, $amount, $gallons, $price) {
        $query = "INSERT INTO gas (date, station, type, amount, gallons, price_per_gallon) 
                 VALUES (:date, :station, :type, :amount, :gallons, :price)";
        
        $stmt = $this->db->prepare($query);
        $stmt->bindValue(':date', $date, PDO::PARAM_STR);
        $stmt->bindValue(':station', $station, PDO::PARAM_STR);
        $stmt->bindValue(':type', $type, PDO::PARAM_STR);
        $stmt->bindValue(':amount', $amount, PDO::PARAM_STR);
        $stmt->bindValue(':gallons', $gallons, PDO::PARAM_STR);
        $stmt->bindValue(':price', $price, PDO::PARAM_STR);
        
        return $stmt->execute();
    }

    public function getAllGasEntries() {
        $query = "SELECT * FROM gas ORDER BY date DESC";
        $stmt = $this->db->query($query);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
}
?>