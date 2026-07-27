export interface CreateExpenseRequest {

    payment_method_id: number | null;

    amount: number;

    amount_type: 'credit' | 'debit';

    expense_date: string;

    notes: string;

}
