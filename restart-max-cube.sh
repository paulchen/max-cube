#!/bin/bash

test_ping() {
	HOST="$1"

	echo -n "Checking whether $1 is online... "
	ping -c 1 "$HOST" > /dev/null 2>&1 && fail=0 || fail=1
	if [ "$fail" == "0" ]; then
		echo "yes"
	else
		echo "no"
	fi
	return "$fail"
}

HOST="$1"

test_ping "$HOST"

echo 'Sending reboot command'

echo -ne 'eQ3Max*\0IEN0037234R'|socat - UDP-DATAGRAM:255.255.255.255:23272,broadcast 

echo 'Waiting 5 seconds'
sleep 5

test_ping "$HOST"

echo 'Waiting 60 seconds'
sleep 60

test_ping "$HOST"

