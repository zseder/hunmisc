
use Parse::MediaWikiDump;
$pmwd = Parse::MediaWikiDump->new;
$pages = $pmwd->pages(@ARGV[0]);
binmode(STDOUT, ':utf8');

#print the title and id of each article inside the dump file
while(defined($page = $pages->next)) {
    my $title = $page->title;
    print "%%#PAGE $title\n";
    my $text = $page->text;
    print $$text, "\n";
}
