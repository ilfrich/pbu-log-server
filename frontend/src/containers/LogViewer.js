import { DateTime } from "luxon"
import { mixins, NotificationBar } from "quick-n-dirty-react"
import { util } from "quick-n-dirty-utils"
import React from "react"
import constants from "../constants"
import chroma from "chroma-js"


const style = {
    logLevel: (color, active = true) => ({
        ...mixins.center,
        display: "inline-block",
        background: active ? color : chroma(color).brighten(2).hex(),
        padding: "4px 4px",
        borderRadius: "8px",
        border: "1px solid #ccc",
        fontSize: "12px",
    }),
    loadButton: {
        ...mixins.clickable,
        marginTop: "5px",
        background: "#fff",
        border: "1px solid #ccc",
        padding: "4px 0px",
        width: "80px",
    },
    table: idx => ({
        ...mixins.stripedTable(idx),
        display: "grid",
        gridTemplateColumns: "150px 80px 200px 60px 1fr",
        gridColumnGap: "2px",
    }),
    logger: {
        ...mixins.trimOverflow,
        fontFamily: "monospace",
        fontSize: "12px",
    },  
    message: {
        ...mixins.trimOverflow,
    },
    expandArrow: {
        ...mixins.clickable,
        display: "inline-block",
        marginRight: "10px",
    },
    stacktrace: {
        whiteSpace: "pre-wrap",
    },
    filterAction: marginRight => ({
        ...mixins.clickable,
        position: "absolute",
        top: "7px",
        right: `${marginRight}px`,
    }),
    filterBadge: isActive => ({
        position: "relative",
        display: "inline-block",
        marginTop: "5px",
        marginRight: "5px",
        borderRadius: "8px",
        paddingTop: "4px",
        paddingBottom: "4px",
        paddingRight: "30px",
        paddingLeft: "8px",
        border: "1px solid #ccc",
        background: isActive ? "#999" : "#fff",
        color: isActive ? "#fff" : "#999",
    }),
    favFilterDelete: {
        ...mixins.clickable,
        position: "absolute",
        top: "6px",
        right: "5px",
        fontSize: "12px",
    },
}

const DT_DISPLAY_FORMAT = "dd/MM/yy T:ss"

const transposeDate = (timestamp, timezone) => {
    return DateTime.fromSeconds(timestamp).setZone(timezone).toFormat(DT_DISPLAY_FORMAT)
}

class LogViewer extends React.Component {

    constructor(props) {
        super(props)

        this.state = {
            activeLoggers: [],
            currentDate: DateTime.now(),
            timezone: "UTC",
            messages: {},   // log level > [messages]
            loading: 0,
            expandedTimestamps: [],
            activeFilters: [],
            inactiveFilters: [],
            currentFilter: "",
        }

        this.getFilteredLogMessages = this.getFilteredLogMessages.bind(this)
        this.setDate = this.setDate.bind(this)
        this.setTimezone = this.setTimezone.bind(this)
        this.setFilter = this.setFilter.bind(this)
        this.saveFilter = this.saveFilter.bind(this)
        this.clearFilter = this.clearFilter.bind(this)
        this.deleteFavFilter = this.deleteFavFilter.bind(this)
        this.load = this.load.bind(this)
        this.toggleFilterActive = this.toggleFilterActive.bind(this)
        this.toggleLogger = this.toggleLogger.bind(this)
        this.toggleExpandedTimestamp = this.toggleExpandedTimestamp.bind(this)
    }

    getFilteredLogMessages() {
        const result = []
        const activeFilters = [...this.state.activeFilters]
        if (this.state.currentFilter.trim() !== "") {
            activeFilters.push(this.state.currentFilter)
        }

        this.state.activeLoggers.forEach(level => {
            const messages = this.state.messages[level]
            if (messages == null) {
                return
            }

            // parse name
            messages.forEach(msg => {                
                if (activeFilters.length > 0) {
                    // have to filter messages
                    const nameFilter = activeFilters.map(f => msg.name.includes(f)).includes(true)
                    const msgFilter = activeFilters.map(f => msg.msg.includes(f)).includes(true)
                    if (nameFilter === false && msgFilter === false) {
                        // not matches to far, have check detail for active filter
                        if (msg.detail == null) {
                            return  // skip this message
                        }
                        if (!msg.detail.map(line => activeFilters.map(f => line.includes(f)).includes(true)).includes(true)) {
                            return  // not even the details match
                        }
                    }
                }

                const copy = { ...msg }
                copy.level = level
                copy.logger = copy.name.split(":")[1]
                copy.line = copy.name.split(":")[2]
                result.push(copy)
            })
        })

        return result.sort((a, b) => a.ts - b.ts)
    }

    setDate(ev) {
        const val = ev.target.value
        if (val === "") {
            return
        }
        const dt = DateTime.fromFormat(val, util.DATE_FORMAT)
        this.setState({ currentDate: dt })
    }

    setTimezone(ev) {
        this.setState({ timezone: ev.target.value })
    }

    setFilter(ev) {
        const filterValue = ev.target.value
        this.setState({ currentFilter: filterValue })
    }

    clearFilter() {
        this.setState({ currentFilter: "" })
        this.currentFilter.value = ""
    }

    saveFilter() {
        if (this.state.currentFilter.trim() === "") {
            return  // nothing to save
        }
        this.setState(oldState => ({
            ...oldState,
            activeFilters: oldState.activeFilters.concat(oldState.currentFilter),
            currentFilter: "",
        }))
        this.currentFilter.value = ""
    }

    deleteFavFilter(filter) {
        return () => {
            this.setState(oldState => ({
                ...oldState,
                activeFilters: oldState.activeFilters.filter(f => f !== filter),
                inactiveFilters: oldState.inactiveFilters.filter(f => f !== filter),
            }))
        }
    }

    toggleFilterActive(filter) {
        return () => {
            this.setState(oldState => ({
                ...oldState,
                activeFilters: oldState.activeFilters.includes(filter) ? oldState.activeFilters.filter(f => f !== filter) : oldState.activeFilters.concat(filter),
                inactiveFilters: oldState.inactiveFilters.includes(filter) ? oldState.inactiveFilters.filter(f => f !== filter) : oldState.inactiveFilters.concat(filter),
            }))
        }
    }

    load() {
        if (this.state.activeLoggers.length === 0) {
            this.alert.info("Please select at least one log level to view")
            return
        }

        this.setState(oldState => ({
            ...oldState,
            loading: this.state.activeLoggers.length,
        }), () => {
            this.state.activeLoggers.forEach(logLevel => {
                fetch(`/api/log/messages?${new URLSearchParams({ 
                    "level": logLevel, 
                    "date": util.formatDate(this.state.currentDate),
                    "timezone": this.state.timezone,
                }).toString()}`, {
                    headers: util.getAuthJsonHeader(),
                })  
                    .then(util.restHandler)
                    .then(messageData => {
                        this.setState(oldState => {
                            const { messages } = oldState
                            messages[logLevel] = messageData
                            return {
                                ...oldState,
                                messages,
                                loading: oldState.loading - 1,
                            }
                        })
                    })
                    .catch(() => {
                        this.alert.error(`Failed to load ${logLevel} logs for date ${util.formatDate(this.state.currentDate)}`)
                        this.setState(oldState => ({
                            ...oldState,
                            loading: oldState.loading - 1,
                        }))
                    })
            })
        })
    }

    toggleLogger(logLevel) {
        return () => {
            this.setState(oldstate => ({
                ...oldstate,
                activeLoggers: util.toggleItem(oldstate.activeLoggers, logLevel),
            }))
        }
    }

    toggleExpandedTimestamp(timestamp) {
        return () => {
            this.setState(oldstate => ({
                ...oldstate,
                expandedTimestamps: util.toggleItem(oldstate.expandedTimestamps, timestamp),
            }))
        }
    }

    render() {
        return (
            <div>
                <NotificationBar ref={el => { this.alert = el }} />
                <div style={mixins.flexRow}>
                    <div style={mixins.width(120)}>
                        <input type="date" style={mixins.textInput} onChange={this.setDate} defaultValue={util.formatDate(this.state.currentDate)} />
                    </div>
                    <div style={{ ...mixins.indent(10), ...mixins.width(130) }}>
                        <select style={mixins.dropdown} onChange={this.setTimezone} defaultValue={this.state.timezone}>
                            <option>UTC</option>
                            <option>Australia/Melbourne</option>
                            <option>Europe/Berlin</option>
                            <option>US/Eastern</option>
                            <option>US/Pacific</option>
                        </select>
                    </div>
                    <div style={mixins.indent(10)}>
                        <div style={mixins.vSpacer(6)} />
                        <div style={mixins.flexRow}>
                            {this.props.logLevels.map((level, idx) => (
                                <div key={level} style={mixins.indent(idx === 0 ? 0 : 5)} onClick={this.toggleLogger(level)}>
                                    <div style={{ 
                                        ...style.logLevel(constants.LOG_COLOR[level], this.state.activeLoggers.includes(level)),
                                        ...mixins.clickable,
                                    }}>{level}</div>
                                </div>
                            ))}
                        </div>              
                    </div>
                    <div style={mixins.indent(40)}>
                        <button style={style.loadButton} type="button" onClick={this.state.loading === 0 ? this.load : null}>
                            {this.state.loading ? "Loading" : "Load"}
                        </button>
                    </div>
                </div>
                <div style={mixins.vSpacer(10)} />
                
                <div style={mixins.flexRow}>
                    <div style={mixins.width(300)}>
                        <div style={mixins.relative}>
                            <input type="text" style={mixins.textInput} ref={el => { this.currentFilter = el }} placeholder="Filter logs" onChange={this.setFilter} />
                            <span style={style.filterAction(40)} onClick={this.saveFilter}>&#128190;</span>
                            <span style={style.filterAction(10)} onClick={this.clearFilter}>&#10060;</span>
                        </div>
                    </div>
                    <div style={mixins.indent(15)}>
                        <div style={mixins.flexRow}>
                            {this.state.activeFilters.concat(...this.state.inactiveFilters).map(filter => (
                                <div style={style.filterBadge(this.state.activeFilters.includes(filter))} key={filter}>
                                    <span style={mixins.clickable} onClick={this.toggleFilterActive(filter)}>{filter}</span>
                                    <span style={style.favFilterDelete} onClick={this.deleteFavFilter(filter)}>&#10060;</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
                

                <div style={mixins.vSpacer(10)} />

                <div style={style.table(0)}>
                    <div style={mixins.listHeader}>Date/Time</div>
                    <div style={mixins.listHeader}>Level</div>
                    <div style={mixins.listHeader}>Logger</div>
                    <div style={mixins.listHeader}>Line</div>
                    <div style={mixins.listHeader}>Message</div>
                </div>
                {this.getFilteredLogMessages().map((msg, idx) => (
                    <div key={`${msg.timestamp}-${idx}`} style={style.table(idx)}>
                        <div style={mixins.center}>{transposeDate(msg.ts)}</div>
                        <div style={mixins.center}>
                            <div style={style.logLevel(constants.LOG_COLOR[msg.level])}>{msg.level}</div>
                        </div>
                        <div style={style.logger}>
                            {msg.logger}
                        </div>
                        <div style={mixins.center}>
                            {msg.line}
                        </div>
                        <div>
                            {msg.detail != null ? (
                                <>
                                    {this.state.expandedTimestamps.includes(msg.ts) ? (
                                        <div style={style.expandArrow} onClick={this.toggleExpandedTimestamp(msg.ts)}>&#11167;</div>
                                    ) : (
                                        <div style={style.expandArrow} onClick={this.toggleExpandedTimestamp(msg.ts)}>&#11166;</div>
                                    )}
                                </>                                
                            ) : null}
                            {msg.msg}
                            {msg.detail != null && this.state.expandedTimestamps.includes(msg.ts) ? (
                                <div style={style.logger}>
                                    {msg.detail.map(line => (
                                        <div key={line} style={style.stacktrace}>{line}</div>
                                    ))}
                                </div>
                            ) : null}
                        </div>
                    </div>
                ))}
            </div>
        )
    }
}

export default LogViewer
