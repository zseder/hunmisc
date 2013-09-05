use Encode;
use Encode::Buckwalter;
$utf = decode( "Buckwalter", "fwbr" );

while(<>) {
    print encode("utf-8", decode("Buckwalter", $_));
}

