using Microsoft.AspNetCore.Routing.Constraints;
using Microsoft.EntityFrameworkCore;
using Newtonsoft.Json.Linq;
using Serilog;
using tests;
using tests.Data;
using tests.Model;


var jObject = new JObject();
jObject["key"] = "value";
jObject["key2"] = new JObject();
jObject["key2"]["subkey"] = 5;

Console.WriteLine(jObject.ToString());

Environment.Exit(0);

var builder = WebApplication.CreateSlimBuilder(args);

builder.Configuration.AddEnvironmentVariables();

builder.Services.AddDbContext<AppDbContext>(setup =>
{
    var connectionString = builder.Configuration.GetConnectionString("Default");
    setup
        .UseMySql(connectionString, ServerVersion.AutoDetect(connectionString), mySql =>
            mySql.UseMicrosoftJson()
                .EnableRetryOnFailure())
        .LogTo(Console.WriteLine, LogLevel.Information)
        .EnableSensitiveDataLogging()
        .EnableDetailedErrors();
});

builder.Services.AddMemoryCache();


builder.Services.Configure<RouteOptions>(opt => { opt.SetParameterPolicy<RegexInlineRouteConstraint>("regex"); });

builder.Services.Configure<HostOptions>(options =>
{
    options.ServicesStartConcurrently = true;
    options.ServicesStopConcurrently = true;
    options.ShutdownTimeout = TimeSpan.FromSeconds(10);
});
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddHostedService<BgService>();

builder.Services.AddSwaggerGen();


var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI();
app.UseRouting();


app.UseHttpsRedirection();


app.MapGet("/",
        (ILogger<Program> logger) => { return new SomeModel() { Value = 5 }; })
    .WithName("TestCompileTimeLog")
    .WithOpenApi();

var url = app.Configuration.GetValue("ASPNETCORE_URLS", "http://localhost:5000");
Log.Logger.ForContext<Program>().Information("Server running at {Url}", url);


try
{
    app.Lifetime.ApplicationStopped.Register(Log.CloseAndFlush);
    app.Run();
}
catch (Exception ex)
{
    Log.ForContext<Program>().Fatal(ex, "Unhandled exception");
    await Log.CloseAndFlushAsync();
}