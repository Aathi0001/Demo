export interface UpdateWorkLogRequest {

    project_id: number | null;

    category_id: number | null;

    title: string | null;

    notes: string;

    work_date: string;

    duration: string;

}
