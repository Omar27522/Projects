<?php
class Database {
    private $db;

    public function __construct() {
        try {
            $this->db = new SQLite3('expenses.db');
            $this->createTable();
        } catch (Exception $e) {
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

    public function addExpense($date, $item, $place, $amount, $type) {
        $query = $this->db->prepare('INSERT INTO expenses (date, item, place, amount, type) VALUES (:date, :item, :place, :amount, :type)');
        $query->bindValue(':date', $date, SQLITE3_TEXT);
        $query->bindValue(':item', $item, SQLITE3_TEXT);
        $query->bindValue(':place', $place, SQLITE3_TEXT);
        $query->bindValue(':amount', $amount, SQLITE3_FLOAT);
        $query->bindValue(':type', $type, SQLITE3_TEXT);
        return $query->execute();
    }

    public function getAllExpenses() {
        $query = "SELECT id, date, item, place, amount, type, 
                  strftime('%Y', date) as year,
                  strftime('%m', date) as month,
                  strftime('%d', date) as day
                  FROM expenses 
                  ORDER BY date DESC";
        return $this->db->query($query);
    }

    public function getMonthlyExpenses() {
        $query = "SELECT strftime('%Y-%m', date) as month,
                  date, item, place, amount, type
                  FROM expenses 
                  ORDER BY date DESC";
        return $this->db->query($query);
    }

    public function getExpenseById($id) {
        $query = $this->db->prepare('SELECT * FROM expenses WHERE id = :id');
        $query->bindValue(':id', $id, SQLITE3_INTEGER);
        $result = $query->execute();
        return $result->fetchArray(SQLITE3_ASSOC);
    }

    public function updateExpense($id, $date, $item, $place, $amount, $type) {
        $query = $this->db->prepare('UPDATE expenses SET date = :date, item = :item, place = :place, amount = :amount, type = :type WHERE id = :id');
        $query->bindValue(':id', $id, SQLITE3_INTEGER);
        $query->bindValue(':date', $date, SQLITE3_TEXT);
        $query->bindValue(':item', $item, SQLITE3_TEXT);
        $query->bindValue(':place', $place, SQLITE3_TEXT);
        $query->bindValue(':amount', $amount, SQLITE3_FLOAT);
        $query->bindValue(':type', $type, SQLITE3_TEXT);
        return $query->execute();
    }

    public function deleteExpense($id) {
        $query = $this->db->prepare('DELETE FROM expenses WHERE id = :id');
        $query->bindValue(':id', $id, SQLITE3_INTEGER);
        return $query->execute();
    }

    public function getDistinctTypes() {
        $query = "SELECT DISTINCT type FROM expenses ORDER BY type ASC";
        $result = $this->db->query($query);
        $types = [];
        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            $types[] = $row['type'];
        }
        return $types;
    }

    public function getDistinctYears() {
        $query = "SELECT DISTINCT strftime('%Y', date) as year FROM expenses ORDER BY year DESC";
        $result = $this->db->query($query);
        $years = [];
        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
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
        $query->bindValue(':monthPattern', $monthStr . '-%', SQLITE3_TEXT);
        if ($type) {
            $query->bindValue(':type', $type, SQLITE3_TEXT);
        }
        
        $result = $query->execute();
        $expenses = [];
        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            $expenses[] = $row;
        }
        return $expenses;
    }

    public function getExpensesByMonthYear($month, $year) {
        $query = "SELECT * FROM expenses 
                 WHERE date LIKE :yearMonth || '%'
                 ORDER BY date DESC";
        try {
            $stmt = $this->db->prepare($query);
            $yearMonth = $year . '-' . str_pad($month, 2, '0', STR_PAD_LEFT);
            $stmt->bindValue(':yearMonth', $yearMonth, SQLITE3_TEXT);
            return $stmt->execute();
        } catch (Exception $e) {
            echo "Error: " . $e->getMessage();
            return null;
        }
    }

    public function getYearlyExpenses() {
        $query = "SELECT id, date, item, place, amount, type FROM expenses ORDER BY date DESC";
        return $this->db->query($query);
    }

    public function getYearlyExpensesSummary() {
        $query = "SELECT strftime('%Y', date) as year, 
                  SUM(amount) as total_amount,
                  COUNT(*) as transaction_count
                  FROM expenses 
                  GROUP BY year 
                  ORDER BY year DESC";
        return $this->db->query($query);
    }

    public function getMonthlyExpensesSummary() {
        $query = "SELECT strftime('%Y-%m', date) as month, 
                  SUM(amount) as total_amount,
                  COUNT(*) as transaction_count
                  FROM expenses 
                  GROUP BY month 
                  ORDER BY month DESC";
        return $this->db->query($query);
    }

    public function getExpensesByYear($year) {
        $query = $this->db->prepare('SELECT * FROM expenses WHERE strftime("%Y", date) = :year ORDER BY date DESC');
        $query->bindValue(':year', $year, SQLITE3_TEXT);
        return $query->execute();
    }
}
?>