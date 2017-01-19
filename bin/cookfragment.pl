#!/usr/bin/env perl
#Remove Permutationally Identical Fragments

while(<STDIN>){
    if(/\@FRAG/){
	my %g;
	print $_;
	$_=<STDIN>;
	print $_;
	while(<STDIN>){
	    chomp;
	    @_ = split;
	    last if $_[0]<0;
	    my $sorted=join(" ",sort @_);
	    if(! defined $g{$sorted}){
		$g{$sorted}=$_;
		print $_,"\n";
	    }
	}
	print $_,"\n";
    }
}
