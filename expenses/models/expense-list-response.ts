import {
    ExpenseModel
} from './expense';

export interface ExpenseListResponse {

    month: string;

    summary: ExpenseSummary;

    weeks: ExpenseWeek[];

}

export interface ExpenseSummary {

    total_credit: number;

    total_debit: number;

    balance: number;

}

export interface ExpenseWeek {

    week: string;

    expenses: ExpenseModel[];

}
