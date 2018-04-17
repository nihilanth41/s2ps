<?php 

require_once "functions.php";

$organization = $_POST["ORG"];	
// Arr is an array containing the new description fields
$Arr = $_POST["id"];
$descCount = count($Arr);
$tmpFile = "uploads/MO_COLUM_{$organization}_UMAP0007.TMP";
$outFile = "uploads/MO_COLUM_{$organization}_UMAP0007.TXT";

if( copy($tmpFile, $outFile) )
{
	$rows = file($outFile);
	$rowCount = count($rows);
	$j=0;
	for($i=0; $i<$rowCount; $i++) 
	{
		if(contains("INSERTDESC", $rows["$i"])) 
		{
			$rows["$i"] = str_replace("INSERTDESC", $Arr["$j"], $rows["$i"]);
			$j++;
		}
	}
	$ret = file_put_contents($outFile, $rows);
	if($ret === false) 
	{
		$outLink = "<a href=\"index.php\">Failed to write file<\a>";
	}
	else 
	{
		$outLink = "<a href=\"{$outFile}\" id=\"download\" download>Download modified file</a>";
	}

	include("template.class.php");
	$header = new Template("header.tpl");
	$header->set("title", "Sierra to PeopleSoft");
	$header->set("heading", "Sierra to PeopleSoft");
	$header->set("subheading", "(LSO) Download");

	$content = new Template("download.tpl");
	$content->set("downloadLink", $outLink);
	
	$footer = new Template("footer.tpl");
	$footer->set("email", "");
	
	$layout = new Template("layout.tpl");
	$layout->set("header", $header->output());
	$layout->set("content", $content->output());
	$layout->set("footer", $footer->output());

	echo $layout->output();
}
else
{
	include("template.class.php");
	$header = new Template("header.tpl");
	$header->set("title", "Sierra to PeopleSoft");
	$header->set("heading", "Sierra to PeopleSoft");
	$header->set("subheading", "Error");

	$content = new Template("error.tpl");
	$content->set("heading", "Server Error");
	$content->set("command", "N/A");
	$content->set("stdout", "Failed to copy temporary file");
	
	$footer = new Template("footer.tpl");
	$footer->set("email", "");
	
	$layout = new Template("layout.tpl");
	$layout->set("header", $header->output());
	$layout->set("content", $content->output());
	$layout->set("footer", $footer->output());

	echo $layout->output();
}

?>
