<?php

function contains($substring, $string) {
	$pos = strpos($string, $substring);
	if($pos == false) {
		return false;
	}
	else {
		return true;
	}
}

function in_arrayi($needle, $haystack) {
	return in_array(strtolower($needle), array_map('strtolower', $haystack)); 
}

function checkArgs($ext, $pDate, $ORGid) {
	$allowed = array('txt', 'out');
	$errString = "";
	if(!(in_arrayi($ext, $allowed))) {
		$errString = "File extension should be one of: [.txt, .out]";
		return array (0, $errString);
	}
	if($pDate == "") {
		$errString = "Date field is empty";
		return array (0, $errString);
	}
	if(!( $ORGid == "LSO" or $ORGid == "CLB" )) {
		$errString = "Organization should be one of: [CLB, LSO]";
		return array (0, $errString);
	}
	return array (1, "");
}

function getTransactions($file) {
	$rows = file($file);
	for($i=1; $i<count($rows); $i++)
	{
		if(contains("INSERTDESC", $rows[$i]))
		{
			$rows[$i] = str_replace("INSERTDESC", "<span style='color:red'>INSERTDESC</span>", $rows[$i]);
			$descPos[] = $i;
		}
	}
	$descCount = count($descPos);
	for($i=0; $i<$descCount; $i++)
	{
		if($i == $descCount-1)
		{
			$transArr[] = array_slice($rows, $descPos[$i]);
		}
		else
		{
			$transArr[] = array_slice($rows, $descPos[$i], ($descPos[$i+1]-$descPos[$i]), true);
		}
	}
	return $transArr;
}

?>
