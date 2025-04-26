#ifndef CALC_ICE
#define CALC_ICE

module Demo
{
  enum operation { MIN, MAX, AVG };
  sequence<long> NumberSequence;

  exception NoInput {};
  exception EmptyListException {};

  struct A
  {
    short a;
    long b;
    float c;
    string d;
  };


  interface Calc
  {
    idempotent long add(int a, int b);
    idempotent long  subtract(int a, int b);
    void op(A a1, short b1);
    idempotent double avg(NumberSequence numbers) throws EmptyListException;
  };
};

#endif