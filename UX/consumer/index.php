<html>
    <head>
        <title>CIS 322 REST-api: Brevets</title>
    </head>

    <body>
        <h1>List of control times</h1>
	<h2> alternating open/close</h2>
        <ul>
            <?php
            $json = file_get_contents('http://api-service/');
            $obj = json_decode($json);
	          $brevets = $obj->All;
            foreach ($obj as $control) {
		foreach ($control as $time) {
                    echo "<li>$time</li>";
		}
            }
            ?>
        </ul>
    </body>
</html>
