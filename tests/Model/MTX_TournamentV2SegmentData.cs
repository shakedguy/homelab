using System.ComponentModel.DataAnnotations.Schema;

namespace tests.Model;

[Table("mtx_tournament_v2_segment_data")]
public record MTX_TournamentV2SegmentData
{
    public int Id { get; set; }

    [Column(TypeName = "json")] public string Globals { get; set; } = string.Empty;

    [Column(TypeName = "json")] public string Actions { get; set; } = string.Empty;

    [Column(TypeName = "json")] public List<BracketRewardDataModel> BracketRewards { get; set; } = [];

    [Column(TypeName = "json")] public string BracketVisuals { get; set; } = string.Empty;

    [Column(TypeName = "json")] public string Visuals { get; set; } = string.Empty;
}