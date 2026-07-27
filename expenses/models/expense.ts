export interface ExpenseModel {

    expense_id: number;

    payment_method_id: number | null;

    payment_method_name: string | null;

    amount: number;

    amount_type: string;

    expense_date: string;

    notes: string;

    delete_status: boolean;

    created_at: string;

    updated_at: string;

}
