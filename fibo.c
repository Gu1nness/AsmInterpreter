struct Fibo {
    int t1;
    int t2;
};

int main() {
    int i = 1, n=127, nextTerm;
    struct Fibo fibo;

    fibo.t1 = 0;
    fibo.t2 = 1;

    while(i<=n) {
        nextTerm = fibo.t1 + fibo.t2;
        fibo.t1 = fibo.t2;
        fibo.t2 = nextTerm;
        i++;
    }
    return fibo.t1;
}
