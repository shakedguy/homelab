using System.Drawing;
using System.Text.Json.Serialization;

namespace tests.Model;

public record SomeModel
{
    public int Value { get; set; }
    
    [JsonIgnore]
    public int ReadonlyValue => Value * Value;

    
    [JsonConverter(typeof(JsonStringEnumConverter))]
    public EColor Color { get; set; } = EColor.Green;
}