export const COUNTRIES = ["BRA", "CAN", "CHN", "EU", "TZA", "USA"] as const;
export const NGOS = ["AMAP", "MFF", "WCPA"] as const;
export const CHAIR = "JPN" as const;

export type CountryId = typeof COUNTRIES[number];
export type NgoId = typeof NGOS[number];
export type RoleId = CountryId | NgoId | typeof CHAIR;
