program example

%%#include <string.h>
%%#include <time.h>
%%#include <stdlib.h>
%%#include <stdio.h>


int myPv1;
assign myPv1 to "{PREFIX}:myPv1";
monitor myPv1;

int myPv2;
assign myPv2 to "{PREFIX}:myPv2";
monitor myPv2;

int myPv3;
assign myPv3 to "{PREFIX}:myPv3";
monitor myPv3;

ss ss2
{

    state state1

    {
		entry
		{
			myPv1=10;
		}

		when (myPv1==myPv2)
		{
			myPv1=0;
		} state state2

		when (myPv1==myPv3)
		{
			myPv1=5;
		} state state3
	}

	state state2

	{
		when (myPv2==myPv3)
		{} state state3

		when (delay(5))
		{} state state3
	}

    state state3

    {
		when (myPv1==0)
		{} state state1

		when (myPv1==myPv2)
		{
			myPv1=0;
		} state state2
	}
}