## Extracts redirect pages (column #6 = 1) from the page database

$6 != "0" {
  gsub(/_/, " ", $3)
  print $3
}
