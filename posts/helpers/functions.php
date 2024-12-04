<?php
function isActiveTab($tabName) {
    return (!isset($_GET['tab']) && $tabName === 'input') || 
           (isset($_GET['tab']) && $_GET['tab'] === $tabName);
}

function getTabClass($tabName) {
    return 'tab' . (isActiveTab($tabName) ? ' active' : '');
}
