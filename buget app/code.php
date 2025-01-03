<?php
    function breadCrumbs(){

        $crumbs = array("🏠","📅","⛽","📈","💵","🏛");
        $links = ["./","#monthlyExpense","#gas","#budget","#tips","#bank"];
        $titles = ["Home", "Monthly Expense", "Gas", "Budget", "Tips", "Bank"];
        for($i=0; $i <= 5; $i++){
        echo "<a href=\"$links[$i]\" title=\"$titles[$i]\"><button>$crumbs[$i]</button></a>";
        }
    }
?>