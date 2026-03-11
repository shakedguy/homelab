namespace tests.Model;

public record BracketRewardDataModel
{
    public int BracketId { get; set; }
    public int MinPlacement { get; set; }
    public string Reward { get; set; }
}