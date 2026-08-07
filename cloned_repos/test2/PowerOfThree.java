//Leetcode 326 sloution
class Solution {
    public boolean isPowerOfThree(int n) 
    {
        int sum = 0;
        while(n!=0)
        {
            sum+=n%10;
            n=n/10;
        }
        if(sum==9)
        {
            return true;
        }
        else
        {
            return false;
        }
    }
}