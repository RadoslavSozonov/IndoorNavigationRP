package com.example.myapplication;

import java.util.Collection;
import java.util.List;

public class Util {

    public static String printList(List list, int start, int end) {
        StringBuilder res = new StringBuilder();

        if (start < 0 || start > end) {
            return "Illegal arguments";
        }

        for (int i=start; i < list.size() && i < end; i++) {
            res.append(list.get(i));
        }

        return res.toString();
    }

    public static String printArray(float[] arr, int start, int end) {
        StringBuilder res = new StringBuilder();

        if (start < 0 || start > end) {
            return "Illegal arguments";
        }

        for (int i=start; i < arr.length && i < end; i++) {
            res.append(arr[i]);
            res.append(", ");
        }

        return res.toString();
    }

}
