#!/bin/bash
printf '%12s %15s  %s\n' Pid Swap\ Usage Command
sort -nk2 < <(
    sed -ne '
        /^Name:/h;
        /^Pid:/H;
        /^VmSwap:/{
          H;
          x;
          s/^.*:\o11\(.*\)\n.*:\o11\(.*\)\n.*:[[:space:]]*\(.*\) kB/           \2           \3  \1/;
          s/^ *\([0-9 ]\{12\}\)\b *\([0-9 ]\{12\}\)\b /\1 \2 kB /p;
          s/^ *[0-9]\+ \+\([0-9]\+\) .*/+\1/;
          w /dev/fd/9' \
              -e '}' /proc/[1-9]*/status 9> >(
        printf 'Total:%19d Kb\n' $(( $( cat ) ))
    )
)