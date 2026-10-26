# Regenerates fictional software fixtures. No database or application changes.
$ErrorActionPreference = 'Stop'
$offices = @(
    @{ id = 'retriever_essentials'; name = 'Retriever Essentials'; baseline = 420; extra = 'food_distributed_lb'; unit = 'lb' },
    @{ id = 'demo_student_support'; name = 'Student Support (Demo Office)'; baseline = 170; extra = 'cases_resolved'; unit = 'cases' },
    @{ id = 'demo_emergency_aid'; name = 'Emergency Aid (Demo Office)'; baseline = 85; extra = 'aid_disbursed_usd'; unit = 'USD' }
)
$seasonality = @(1.10, 1.18, 0.72, 0.55, 1.02, 1.12, 1.16, 0.88, 0.40, 0.32, 0.75, 1.22)
$rows = [Collections.Generic.List[object]]::new()
$recordId = 0
for ($month = 0; $month -lt 12; $month++) {
    $period = [datetime]::new(2025, 10, 1).AddMonths($month)
    foreach ($office in $offices) {
        foreach ($level in @('undergraduate', 'graduate')) {
            $share = if ($level -eq 'undergraduate') { 0.8 } else { 0.2 }
            $interactions = [int][math]::Round($office.baseline * $seasonality[$month] * $share * (1 + $month * 0.012))
            $unique = [int][math]::Round($interactions * 0.68)
            $referrals = [int][math]::Round($interactions * 0.14)
            $extra = switch ($office.id) {
                'retriever_essentials' { [math]::Round($interactions * 6.25, 2) }
                'demo_student_support' { [int][math]::Round($interactions * 0.61) }
                'demo_emergency_aid' { if ($month -eq 9 -and $level -eq 'graduate') { 0 } else { [math]::Round($unique * 125.50, 2) } }
            }
            $values = @(
                @{ metric = 'service_interactions'; unit = 'interactions'; value = $interactions },
                @{ metric = 'unique_students'; unit = 'students'; value = $unique },
                @{ metric = 'referrals_made'; unit = 'referrals'; value = $referrals },
                @{ metric = $office.extra; unit = $office.unit; value = $extra }
            )
            foreach ($item in $values) {
                $recordId++
                $rows.Add([pscustomobject][ordered]@{
                    record_id = $recordId
                    office_id = $office.id
                    office_name = $office.name
                    time_period = $period.ToString('yyyy-MM-dd')
                    period_end = $period.AddMonths(1).AddDays(-1).ToString('yyyy-MM-dd')
                    student_level = $level
                    metric = $item.metric
                    value = $item.value
                    unit = $item.unit
                    is_demo = $true
                })
            }
        }
    }
}
$rows | Export-Csv -LiteralPath (Join-Path $PSScriptRoot 'dashboard_metrics.csv') -NoTypeInformation -Encoding utf8
foreach ($office in $offices) {
    $rows | Where-Object office_id -eq $office.id | Export-Csv -LiteralPath (Join-Path $PSScriptRoot ($office.id + '.csv')) -NoTypeInformation -Encoding utf8
}
[ordered]@{
    schema_version = 1
    is_demo = $true
    description = 'Entirely fictional monthly aggregates for development. Not UMBC operational data.'
    records = @($rows.ToArray())
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'dashboard_metrics.json') -Encoding utf8
Write-Output "Generated $($rows.Count) metric rows across 3 offices and 12 months."
