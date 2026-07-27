export interface ExpenseListRequest {

    search: string;

    payment_method_id: number | null;

    month: string;

    delete_status: boolean;

}
