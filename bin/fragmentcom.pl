#!/usr/bin/env perl

#
#Output the center of mass of each fragment in @AR3A format.
#

use strict;

sub usage{
    die "usage: $0 coord.nx4a < frag.frag\n";
}

sub rint{
  my ( $x ) = @_;
  my $i=0;
  while ( 0.5 <= $x ){
    $i++;
    $x--;
  }
  while ( $x < -0.5 ){
    $i--;
    $x++;
  }
  $i;
}

my $coord = shift || usage();
open COORD, "<$coord" || die "Cannot open $coord.\n";


while(<STDIN>){
    if (/^\@FRAG/ ){
	my ( $bx, $by, $bz );
	my @coord;
	while(<COORD>){
	    if ( /^\@BOX3/ ){
		print $_;
		$_ = <COORD>;
		print $_;
		chomp;
		($bx, $by,$bz ) = split;
	    }
	    elsif( /^\@NX4A/ || /^\@AR3A/ ){
		my $n = <COORD>;
		foreach my $i ( 0.. $n-1 ){
		    $_ = <COORD>;
		    chomp;
		    my ( $x,$y,$z) = split;
		    if ( $bx ){
			$x -= rint($x/$bx)*$bx;
			$y -= rint($y/$by)*$by;
			$z -= rint($z/$bz)*$bz;
		    }
		    $coord[ $i ] = [ $x,$y,$z ];
		}
		last;
	    }
	}
	$_ = <STDIN>;
	chomp;
	print "\@FCOM\n";
	my @lines;
	my ( $m,$n ) = split;
	while(<STDIN>){
	    chomp;
	    my @members = split;
	    last if $members[0] < 0;
	    #print;
	    my @co;
	    my @sum;
	    my $first = $members[0];
	    foreach my $member ( @members ){
		my $dx = $coord[$member][0] - $coord[$first][0];
		my $dy = $coord[$member][1] - $coord[$first][1];
		my $dz = $coord[$member][2] - $coord[$first][2];
		if ( $bx ){
		    $dx -= rint( $dx / $bx ) * $bx;
		    $dy -= rint( $dy / $by ) * $by;
		    $dz -= rint( $dz / $bz ) * $bz;
		}
		$co[$member][0] = $dx;
		$co[$member][1] = $dy;
		$co[$member][2] = $dz;
		$sum[0] += $co[$member][0];
		$sum[1] += $co[$member][1];
		$sum[2] += $co[$member][2];
	    }
	    $sum[0] /= $m;
	    $sum[1] /= $m;
	    $sum[2] /= $m;
	    push @lines, join( " ",
			$coord[$first][0]  + $sum[0],
			$coord[$first][1]  + $sum[1],
			$coord[$first][2]  + $sum[2] ) . "\n";
	}
	print $#lines+1, "\n", join( "", @lines );
    }
    else{
	print $_;
    }
}



