export interface UserInfo {
  email: string | null;
  user_id: string | null;
  username: string | null;
}

export interface ClientSearchResult {
  koo_clientid: string;
  koo_contactid: string | null;
  client_name: string;
  client_nhi: string | null;
  create_date: string | null;
  response_house: string | null;
  response_impa: string | null;
  response_mmh: string | null;
}

export interface SearchResponse {
  results: ClientSearchResult[];
  total: number;
}

export interface SearchFilters {
  client_name: string;
  client_nhi: string;
  start_date: Date | null;
  end_date: Date | null;
}

export interface ReportData {
  koo_clientid: string;
  client_name: string | null;
  client_nhi: string | null;
  dhb: string | null;
  domicile: string | null;
  gender: string | null;
  ethnicity: string | null;
  primary_caregiver: string | null;
  well_child_level_of_need: string | null;
  housing_concerns: number | null;
  housing_risk_categories: string | null;
  is_disability_discussed: number | null;
  disability_categories: string | null;
  family_member_disability: string | null;
  mmh_concerns: number | null;
  mental_health_categories: string | null;
  family_mental_concerns: number | null;
  family_mental_health_categories: string | null;
  family_member_impact: string | null;
  house_summary: string | null;
  impa_summary: string | null;
  mmh_summary: string | null;
}   