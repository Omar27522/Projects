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
        $query = "SELECT * FROM expenses ORDER BY date DESC";
        $result = $this->db->query($query);
        $expenses = [];
        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            $expenses[] = $row;
        }
        return $expenses;
    }

    public function deleteExpense($id) {
        $query = $this->db->prepare('DELETE FROM expenses WHERE id = :id');
        $query->bindValue(':id', $id, SQLITE3_INTEGER);
        return $query->execute();
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
}
?>