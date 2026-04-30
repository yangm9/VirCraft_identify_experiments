#!/usr/bin/env perl
use strict;
use warnings;
use threads;
use Thread::Queue;

my ($input, $outdir, $threads_num) = @ARGV; # nonviral-common-random-fragments.ftr, nonviral_genomes, 32
$threads_num ||= 32; 
mkdir $outdir unless -d $outdir;

# ================== read file and process ID ==================
my %seen;
my @ids;

open my $fh, '<', $input or die "Cannot open $input: $!\n";
while (<$fh>) {
    chomp;
    my ($id) = split /\|\|/;
    next unless defined $id;
    next if $id =~ /contig_size/;
    next if $id =~ /^\s*$/;
    next if $seen{$id}++;
    push @ids, $id;
}
close $fh;

# ================== create queue ==================
my $queue = Thread::Queue->new(@ids);

# ================== work thread function ==================
sub worker {
    while (defined(my $id = $queue->dequeue_nb)) {
        my $outfile = "$outdir/$id.fasta";
        my $cmd = "efetch -db nucleotide -format fasta -id $id > $outfile";
        system($cmd) == 0
            or warn "Failed to fetch $id\n";
    }
}

# ================== start thread ==================
my @threads;
for (1 .. $threads_num) {
    push @threads, threads->create(\&worker);
}

# ================== wait foe the thread finished ==================
$_->join for @threads;

print "All downloads finished.\n";
