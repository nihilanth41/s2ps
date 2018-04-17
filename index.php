<?php 
	include("template.class.php");

	$header = new Template("header.tpl");
	$header->set("title", "Sierra to PeopleSoft");
	$header->set("heading", "Sierra to PeopleSoft");
	$header->set("subheading", "File upload");

	$content = new Template("index.tpl");
	
	$footer = new Template("footer.tpl");
	$footer->set("email", "");

	$layout = new Template("layout.tpl");
	$layout->set("header", $header->output());
	$layout->set("content", $content->output());
	$layout->set("footer", $footer->output());

	echo $layout->output();
?>






