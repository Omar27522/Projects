<!DOCTYPE html>
<html>
<head>
    <title>Alternative Syntax for Control Structures</title>
    <style>
        body { background: linear-gradient(-45deg, #4E6AFF, #72FFA6, #FF5E5E, #FFC371, #FFD700, #8A2BE2); background-size: 400% 400%; animation: gradient 15s ease infinite; height: 100vh;}
        @keyframes gradient { 0% {     background-position: 0% 50%; } 50% {     background-position: 100% 50%; } 100% {     background-position: 0% 50%; } }
        h1 { color: #3F51B5; /* Dark blue */ background-color: #FFC107; /* Amber */ padding: 10px 20px; /* Add padding for better visibility */ border-radius: 10px; /* Add rounded corners */ box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); /* Add a subtle shadow */}
        h2 { margin-top:44%; color: #9C27B0; /* Purple */ background-color: #4CAF50; /* Green */ padding: 10px 20px; /* Add padding for better visibility */ border-radius: 10px; /* Add rounded corners */ box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); /* Add a subtle shadow */}
        h6 { display:inline; color: #4CAF50; /* Green */ background-color: #FF5722; /* Deep Orange */ padding: 5px 10px; /* Add padding for better visibility */ border-radius: 5px; /* Add rounded corners */ box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1); /* Add a subtle shadow */}
        span {float:right;padding-right: 20px;}
        pre {background-color: lightgrey; display: inline-block;}
        ul {list-style-type: none; padding: 0;}
        li {vertical-align: top; display: inline-block; position: relative;padding: 5px;}
        #if {background-color: lightgreen;}
        #while {background-color: lightblue;}
        #for {background-color: lightcoral;}
        #foreach {background-color: lightgoldenrodyellow;}
        #switch {background-color: lightpink;}
        #if-alt {background-color: aquamarine;}
        #while-alt {background-color: aqua;}
        #for-alt {background-color: #FFD700;} /* Gold */
        #foreach-alt {background-color: #FF6347;} /* Tomato */
        #switch-alt {background-color: #9370DB;} /* MediumPurple */
        footer{margin-top:3%;position:relative;top:0;padding-top:.5rem;  }
        details {
            background-color: #1a1a1a;
            display: inline-block;
            float: right;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.4);
        }

        summary {
            background: linear-gradient(to bottom, #333, #000);
            color: white;
            font-size: 25px;
            display: inline-block;
            float: right;
            padding: 15px 30px;
            border-radius: 10px;
            cursor: pointer;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.6);
            transition: transform 0.2s ease; /* Smooth transition effect */
            animation: pulse 2s infinite alternate; /* Added pulse animation */
        }

        @keyframes pulse {
            from {
                transform: scale(1);
            }
            to {
                transform: scale(1.05); /* Slightly larger scale for pulse effect */
            }
        }

        summary:hover {
            transform: translateY(-3px);
        }

        summary:active {
            color: lightblue;
        }
    </style>
    <meta name ="viewport" content = "width = device-width, initial-scale=1.0"/>
</head>
<body>
    <header>
        <h1>Alternative syntax for control structures</h1>
     <details><summary>Link</summary>
    <a title="Alternative Syntax for Control Structures"
    href="https://www.php.net/manual/en/control-structures.alternative-syntax.php">
    <h6>https://www.php.net/manual/en/control-structures.alternative-syntax.php</h6></a>
    </details>
    </header>
    <article>
    <section>
    <h2>Control Structures</h2>
    <h4>$var=2;</h4><h4>$array = array(1, 2, 3, 4, 5);</h4>
    <ul>
        <li><pre id="if"><strong>If:</strong>&nbsp;&nbsp;&nbsp;&nbsp;if ($var == 2)
          {
              echo TRUE;
          }</pre>
        </li>
        <li><pre id="while"><strong>While:</strong>&nbsp;&nbsp;&nbsp;&nbsp;while ($var == 2)
            {
                echo TRUE;
                return 0;
            }</pre>
        </li>
        <li><pre id="for"><strong>For:</strong>&nbsp;&nbsp;&nbsp;&nbsp;for ($i = 0; $i < 10; $i++)
            {
                echo $i;
            }</pre>
        </li>
        <li><pre id="foreach"><strong>Foreach:</strong>&nbsp;&nbsp;&nbsp;&nbsp;foreach ($array as $value)
            {
                echo $value;
            }</pre>
        </li>
        <li><pre id="switch"><strong>Switch:</strong>&nbsp;&nbsp;&nbsp;&nbsp;switch ($var)
            {
                case 1:
                    echo "One";
                    break;
                case 2:
                    echo "Two";
                    break;
                default:
                    echo "Other";
            }</pre>
        </li>
    </ul><section>
    <?php
     $var = 2;
     $array = array(1, 2, 3, 4, 5);
     // If statement
     if ($var == 2) {
         echo '<b>If</b> is true because $var is ' . TRUE . '<br />';
     }
     // While loop
     echo '<b>While:</b> ';
     while ($var == 2) {
         echo 'Looping... ';
         break; // Break the loop to avoid infinite execution
     }
     echo '<br />';
     // For loop
     echo '<b>For:</b> ';
     for ($i = 0; $i < 10; $i++) {
         echo $i . ' ';
     }
     echo '<br />';
     // Foreach loop
     echo '<b>Foreach:</b> ';
     foreach ($array as $value) {
         echo $value . ' ';
     }
     echo '<br />';
     // Switch statement
     echo '<b>Switch:</b> ';
     switch ($var) {
         case 1:
             echo "One";
             break;
         case 2:
             echo "Two";
             break;
         default:
             echo "Other";
     }
    ?>
    <p><hr></p>
    </section>
    <section>
        <h2>Alternative Syntax</h2>
     <ul>
        <li>
            <pre><strong>If->->-> </strong><span id="if-alt">if ($var == 2) : echo TRUE; endif;</span></pre></li><br />
        <li>
            <pre><strong>While->->-> </strong><span id="while-alt">while ($var == 2): echo TRUE; return 0; endwhile;</span></pre></li><br />
        <li>
            <pre><strong>For->-> </strong><span id="for-alt">for ($i = 0; $i < 10; $i++) : echo $i; endfor;</span></pre></li><br />
        <li>
            <pre><strong>Foreach-> </strong><span id="foreach-alt">foreach ($array as $value) : echo $value; endforeach;</span></pre></li><br />
        <li>
            <pre><strong>Switch-> </strong><span id="switch-alt">switch ($var) :
            case 1: echo "One"; break;
            case 2: echo "Two"; break;
         default: echo "Other"; endswitch;</span></pre></li><br />
     </ul>
    <?php
        echo '<b>If: </b> ';
    if ($var == 2) : echo TRUE; endif;
        echo '<br />';

        echo '<b>While: </b> ';
    while ($var == 2) : echo 'Looping... '; break; endwhile;
        echo '<br />';

        echo '<b>For: </b> ';
    for ($i = 0; $i < 10; $i++) : echo $i; endfor;
        echo '<br />';
        echo '<b>Foreach: </b> ';
    foreach ($array as $value) : echo $value; endforeach;
        echo '<br />';

        echo '<b>Switch: </b> ';
    switch ($var) :
        case 1: echo "One"; break;
        case 2: echo "Two"; break;
        default: echo "Other";
    endswitch;
    ?><p><hr></p></section></article>
    <footer>   <span>Tenes</span>
    </footer>
</body>
</html>