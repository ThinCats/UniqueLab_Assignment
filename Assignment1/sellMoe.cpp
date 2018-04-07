//
// ─── PESUCODE ───────────────────────────────────────────────────────────────────
//

/*
    def SellMoe(plist[], days):
        set F[days-1][days-1];
        for i=0 to days:
            for v=1 to i:
                F[i, v] = Max(F[i-1, v-1]-plist[i], F[i-1, v+1]+plist[i])
        return F[days-1, 0]

*/

// ────────────────────────────────────────────────────────────────────────────────

#include <iostream>

using namespace std;

int Max(int a, int b) {
    return a>b?a:b;
}

/**
 * Core Function
 */
int SellMoe(int plist[], int days) {
    int F[days][days];
    F[0][0] = 0;
    F[0][1] = -plist[0];
    for(int i=1;i < days;i++)
    {   
         if((i+1) % 2 == 0) {
            F[i][0] =  F[i-1][1] + plist[i];
            }                   // v = 0 只有 i+1为偶数才满足
        for(int v=1;v <= i + 1;v++) {
            if(((i+v)%2 == 0))  //如果同奇偶
            {
                F[i][v] = INT32_MIN;
                continue;
            }  // 不可能存在同奇偶情况
            else if(v + 1  > i )  // 爆仓了 (对应i-1的仓数最大为i)
                F[i][v] =  F[i-1][v-1] - plist[i];
            else
                F[i][v] = Max(F[i-1][v-1]-plist[i], F[i-1][v+1]+plist[i]);
            //cout << "i = " << i << " v= " << v << " F[i][v] " << F[i][v] << " F[i-1][v-1] " << F[i-1][v-1] << " F[i-1][v+1] " << F[i-1][v+1] <<endl;
        }
    }
/*
    //debug
    for(int i=0;i < days;i++)
    {
        for(int j=0;j <= i + 1;j++)
            cout << "F[" << i << "][" << j << "] = " << F[i][j] << " "; 
        cout << endl;
    }
*/
    //find Max
    int max = 0;
    for(int i=1; i < days-1;i++) {
        if(F[days-1][max] < F[days-1][i])
            max = i;
    }
    return F[days-1][max];
}



int ListLen(int plist[]) {
    int len = 0;
    while(*(plist++) != -1)
        len ++;
    return len;
}

int *Str2int(char *s) {
    static int plist[1001];
    int *tmp = plist;
    while(*s != '\0') {
        if(*s == ' ') {
            s++;
            continue;
        }
            
        *tmp++ = *s++ - '0';
    }
    *tmp = -1;
    return plist;

}

int main(void) {

    //int plist[] = {92, 25, 43, 77, 76, 20, 69, 13, 49, 96, 62, 41, 6, 49, 72, -1};
    char s[1001];
    cin.getline(s, 1000);
    int *tmp = Str2int(s);
    //cout << SellMoe(plist, sizeof(plist)/sizeof(plist[0])) << endl;
    //cout << tmp[0] << " " << tmp[1] << endl;
    cout << SellMoe(tmp, ListLen(tmp)) << endl;
    return 0;
}