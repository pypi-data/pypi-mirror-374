def sort_indicators(deduped_indicators):
    return sorted(deduped_indicators,
                  key=lambda indicator: (
                      indicator.term.termType,
                      indicator.term.id,
                      indicator.key.id if indicator.key else "",
                      indicator.country.id if indicator.country else "",
                      indicator.landCover.id if indicator.landCover else "",
                      indicator.previousLandCover.id if indicator.previousLandCover else "",
                      tuple({i.id for i in indicator.inputs}) if indicator.inputs else "",
                      indicator.value *-1
                  ), reverse=False)
